"""Magnetic"""

from pymatgen.core import Structure
from pymatgen.analysis.magnetism import MagneticStructureEnumerator

from aiida.engine import calcfunction, WorkChain, if_, ToContext
from aiida import orm
from aiida.plugins import CalculationFactory
from aiida.common import AttributeDict

SupercellCalculation = CalculationFactory('supercell')


@calcfunction
def magnetic_enumeration(structure: orm.StructureData, strategies: orm.List, automatic: orm.Bool) -> orm.StructureData:
    """calcfuntion to perform magnetic enumeration

    Args:
        structure (orm.StructureData): [description]
        strategies (orm.List): [description]
        automatic (orm.Bool): [description]

    Returns:
        orm.StructureData: [description]
    """
    strc = structure.get_pymatgen_structure()
    mag_confs = MagneticStructureEnumerator(structure=strc, strategies=strategies.get_list(), automatic=automatic.value)
    mag_strc_dict = {}
    for index, (mag_ordr,
                mag_strc) in enumerate(zip(mag_confs.ordered_structure_origins, mag_confs.ordered_structures)):
        mag_strc.sort()
        mag_strc_dict[f'{mag_ordr}_{index}'] = orm.StructureData(
            pymatgen_structure=mag_strc, label=f'{mag_ordr}_{index}'
        )

    return mag_strc_dict


class MagneticStructureWorkChain(WorkChain):
    """MagneticStructureWorkChain
    """

    @classmethod
    def define(cls, spec):
        super().define(spec)

        spec.expose_inputs(SupercellCalculation, exclude=['structure'], namespace='supercell')
        spec.input('structure', valid_type=(orm.SinglefileData, orm.StructureData), required=True, help='StructureData')
        spec.input(
            'default_magmoms',
            valid_type=orm.Dict,
            required=True,
            help='A string or list of strings of magnetic elements'
        )
        spec.input(
            'strategies', valid_type=orm.List, default=lambda: orm.List(list=['ferromagnetic', 'antiferromagnetic'])
        )
        spec.input('automatic', valid_type=orm.Bool, default=lambda: orm.Bool(True))
        spec.input(
            'selection_criteria',
            valid_type=orm.Str,
            required=False,
            help='How to select one structure from enumeration'
        )

        spec.outline(
            cls.initialize,
            if_(cls.should_run_supercell)(cls.run_supercell), cls.run_magnetic_enumeration, cls.results
        )

        spec.output_namespace('magnetic_structures', valid_type=orm.StructureData, dynamic=True)

    def initialize(self):
        """Initialize the input parameters
        """
        self.ctx.should_run_supercell = bool('selection_criteria' in self.inputs)
        if self.ctx.should_run_supercell:
            self.ctx.sample_structures = {self.inputs.selection_criteria.value: 1}

        if isinstance(self.inputs.structure, orm.SinglefileData) and not self.ctx.should_run_supercell:
            cif_str = self.inputs.structure.get_content()
            strc_pmg = Structure.from_str(cif_str, fmt='cif')
            self.ctx.structure = orm.StructureData(pymatgen_structure=strc_pmg)
        else:
            self.ctx.structure = self.inputs.structure

    def should_run_supercell(self):
        return self.ctx.should_run_supercell

    def run_supercell(self):
        """Prepare and run SupercellCalculation"""
        self.ctx.supercell = AttributeDict(self.exposed_inputs(SupercellCalculation, 'supercell'))
        self.ctx.supercell.structure = self.ctx.structure
        self.ctx.supercell.sample_structures = orm.Dict(dict=self.ctx.sample_structures)
        self.ctx.supercell['metadata'].update({
            'label': 'SupercellCalculation',
            'call_link_label': 'run_SupercellCalculation'
        })
        running = self.submit(SupercellCalculation, **self.ctx.supercell)
        self.report(f'Submitted SupercellCalculation')
        return ToContext(enum=running)

    def run_magnetic_enumeration(self):
        """Prepare and run magnetic enumeration"""
        if self.ctx.should_run_supercell:
            self.ctx.structure = self.ctx.enum.outputs.output_structures[next(
                iter(self.ctx.enum.outputs.output_structures)
            )]

        self.ctx.mag_strcs = magnetic_enumeration(self.ctx.structure, self.inputs.strategies, self.inputs.automatic)

    def results(self):
        for key, value in self.ctx.mag_strcs.items():
            self.out(f'magnetic_structures.{key}', value)

        self.report('MagneticStructureWorkChain has finished successfully!')


# EOF
