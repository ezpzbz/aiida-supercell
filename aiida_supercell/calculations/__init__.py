"""AiiDA-Supercell plugin"""

import os

from aiida.engine import CalcJob
from aiida.plugins import DataFactory
from aiida.orm import Dict, Int, Bool, Str, List, Float, StructureData, SinglefileData
from aiida.common import CalcInfo, CodeInfo, exceptions

# StructureData = DataFactory('structure')
# SinglefileData = DataFactory('singlefile')


class SupercellCalculation(CalcJob):
    """
    This is a SupercellCalculation, subclass of JobCalculation,
    to prepare input for enumerating structures using Supercell program
    """

    _INPUT_FILE = 'aiida.cif'
    _OUTPUT_FOLDER = 'Output'
    _OUTPUT_FILE_PREFIX = 'aiida_supercell'
    _OUTPUT_FILE = 'output.log'
    _PARSER = 'supercell'

    @classmethod
    def define(cls, spec):
        super(SupercellCalculation, cls).define(spec)

        # Input parameters
        spec.input('structure', valid_type=(StructureData, SinglefileData), required=True, help='Input structure')
        spec.input('random_seed', valid_type=Int, required=False, help='Random seed number')
        spec.input('charges', valid_type=Dict, required=False, help='Dictionary of formal charges to be used')
        spec.input(
            'calculate_coulomb_energies', valid_type=Bool, required=False, help='Whether to calculate Coulomb energies'
        )
        spec.input('charge_balance_method', valid_type=Str, required=False, help='Method to use for charge balancing')
        spec.input(
            'merge_symmetric',
            valid_type=Bool,
            required=False,
            help='Whether to merge symmetrically distinct configurations'
        )
        spec.input(
            'tolerance',
            valid_type=Float,
            default=lambda: Float(0.75),
            required=False,
            help='The maximum distance (in Angstroms) between sites that should be contained within the same group.'
        )
        spec.input('supercell_size', valid_type=List, required=True, help='Supercell size for enumeration')
        spec.input(
            'save_as_archive', valid_type=Bool, required=False, help='Whether to save resulting structures as archive'
        )
        spec.input(
            'sample_structures',
            valid_type=Dict,
            required=False,
            help='How to sample structures from huge configuration space'
        )

        spec.input('metadata.options.withmpi', valid_type=bool, default=False)

        # Set parser name to the metadata
        spec.input('metadata.options.parser_name', valid_type=str, default=cls._PARSER, non_db=True)

        # Add output_filename attribute to the metadata
        spec.input('metadata.options.output_filename', valid_type=str, default=cls._OUTPUT_FILE)

        # Exit codes
        spec.exit_code(
            100, 'ERROR_NO_RETRIEVED_FOLDER', message='The retrieved folder data node could not be accessed.'
        )
        spec.exit_code(101, 'ERROR_ON_INPUT_STRUCTURE', message='Input structure could not be processed.')

        # Output parameters
        spec.output('output_parameters', valid_type=Dict, required=True, help='the results of the calculation')
        spec.output_namespace(
            'output_structures', valid_type=StructureData, required=True, dynamic=True, help='relaxed structure'
        )

    # pylint: disable=too-many-statements,too-many-branches
    def prepare_for_submission(self, folder):
        """Create the input files from the input nodes passed to this instance of the `CalcJob`.
        :param folder: an `aiida.common.folders.Folder` to temporarily write files on disk
        :return: `aiida.common.datastructures.CalcInfo` instance
        """

        try:
            self._write_structure(self.inputs.structure, folder)
        except exceptions.FailedError:
            self.exit_codes.ERROR_ON_INPUT_STRUCTURE  # pylint: disable=no-member, pointless-statement

        # get settings
        settings = self.inputs.settings.get_dict() if 'setting' in self.inputs else {}
        cmdline_arguments = ['-i', self._INPUT_FILE]
        if 'supercell_size' in self.inputs:
            s = self.inputs.supercell_size
            cmdline_arguments.append(f'-s {s[0]}x{s[1]}x{s[2]}')

        if self.inputs.merge_symmetric:
            cmdline_arguments.append('-m')

        cmdline_arguments.append('-t')
        cmdline_arguments.append(self.inputs.tolerance.value)

        if self.inputs.calculate_coulomb_energies:
            cmdline_arguments.append('-q')
            cmdline_arguments.append('-g')
            cmdline_arguments.append(f'-c {self.inputs.charge_balance_method.value}')

        if 'random_seed' in self.inputs:
            cmdline_arguments.append(f'--random-seed={self.inputs.random_seed.value}')

        if 'charges' in self.inputs:
            charges = self.inputs.charges.get_dict()
            for key, value in charges.items():
                arg = '-p ' + key + ':c=' + str(value)
                cmdline_arguments.append(arg)
        if 'sample_structures' in self.inputs:
            for key, value in self.inputs.sample_structures.get_dict().items():
                if key == 'low_energy':
                    cmdline_arguments.append('-n')
                    cmdline_arguments.append(f'l{value}')
                if key == 'high_energy':
                    cmdline_arguments.append('-n')
                    cmdline_arguments.append(f'h{value}')
                if key == 'random':
                    cmdline_arguments.append('-n')
                    cmdline_arguments.append(f'r{value}')
                if key == 'first':
                    cmdline_arguments.append('-n')
                    cmdline_arguments.append(f'f{value}')
                if key == 'last':
                    cmdline_arguments.append('-n')
                    cmdline_arguments.append(f'a{value}')
                if key == 'degeneracy':
                    cmdline_arguments.append('-n')
                    cmdline_arguments.append(f'w{value}')

        if not self.inputs.save_as_archive:
            cmdline_arguments.append('-o')
            cmdline_arguments.append(f'{self._OUTPUT_FOLDER}/{self._OUTPUT_FILE_PREFIX}')
        else:
            cmdline_arguments.append('-a')
            cmdline_arguments.append(f'{self._OUTPUT_FOLDER}/{self._OUTPUT_FILE_PREFIX}.tar.gz')

        # create code info
        codeinfo = CodeInfo()
        codeinfo.cmdline_params = settings.pop('cmdline', []) + cmdline_arguments
        codeinfo.join_files = True
        codeinfo.code_uuid = self.inputs.code.uuid
        codeinfo.stdout_name = self._OUTPUT_FILE

        # create calc info
        calcinfo = CalcInfo()
        calcinfo.uuid = self.uuid
        calcinfo.cmdline_params = codeinfo.cmdline_params
        calcinfo.codes_info = [codeinfo]

        # Retrive list
        calcinfo.retrieve_list = [('./Output', '.', 0), self._OUTPUT_FILE]
        if self.inputs.calculate_coulomb_energies:
            calcinfo.retrieve_list += [('./Output/aiida_supercell*.txt', '.', 0)]
        if 'save_as_archive' in self.inputs:
            if self.inputs.save_as_archive:
                calcinfo.retrieve_list += [('./Output/aiida_supercell.tar.gz', '.', 0)]
        calcinfo.retrieve_list += settings.pop('additional_retrieve_list', [])

        # Create output directory
        os.makedirs(folder.get_abs_path(self._OUTPUT_FOLDER))

        return calcinfo

    @staticmethod
    def _write_structure(structure, folder):
        """Function that writes a structure and takes care of element tags"""
        path = os.path.join(folder.get_abs_path('aiida.cif'))
        if isinstance(structure, SinglefileData):
            cif_content = structure.get_content()
            with open(path, mode='w') as fobj:
                fobj.write(cif_content)
        elif isinstance(structure, StructureData):
            strc_pmg = structure.get_pymatgen_structure()
            strc_pmg.to(fmt='cif', filename=path)


#EOF
