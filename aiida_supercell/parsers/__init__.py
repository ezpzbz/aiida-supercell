"""AiiDA-Supecell plugin -- Supercell Parser"""

from collections import defaultdict
from pymatgen.core import Structure
from pymatgen.symmetry.analyzer import SpacegroupAnalyzer

from aiida.common import exceptions
from aiida.parsers import Parser
from aiida.orm import Dict
from aiida.engine import ExitCode
from aiida.plugins import DataFactory
from aiida_supercell.utils import parse_supercell_output

StructureData = DataFactory('structure')


class SupercellParser(Parser):
    """Parser for Supercell Calculations"""

    def parse(self, **kwargs):
        """Receives in input a dictionary of retrieved nodes. Does all the logic here.
        """

        try:
            _ = self.retrieved
        except exceptions.NotExistent:
            return self.exit_codes.ERROR_NO_RETRIEVED_FOLDER

        exit_code = self._parse_stdout()
        if exit_code is not None:
            return exit_code

        return ExitCode(0)

    def _parse_stdout(self):  # pylint: disable=too-many-locals
        """Supercell Basic Output parser"""

        fname = self.node.get_attribute('output_filename')

        if fname not in self.retrieved.list_object_names():
            return self.exit_codes.ERROR_OUTPUT_STDOUT_MISSING

        try:
            output_string = self.retrieved.get_object_content(fname)
        except IOError:
            return self.exit_codes.ERROR_OUTPUT_STDOUT_READ

        output_list = self.retrieved.list_object_names(path='Output')

        enrg_outputs = []
        for o in output_list:
            if 'aiida_supercell_coulomb_energy_' in o:
                enrg_outputs.append(o)

        result_dict = parse_supercell_output(output_string)

        s_dict = defaultdict(dict)
        res_dict = defaultdict(lambda: defaultdict(lambda: defaultdict(dict)))

        if len(enrg_outputs) > 0:
            res_dict['coulombic_energy_unit'] = 'eV'
            enrg_content = ''
            for item in enrg_outputs:
                enrg_content += self.retrieved.get_object_content(item)

            for i in enrg_content.split('\n')[:-1]:
                sp = i.split()
                enrg = float(sp[1])
                label = sp[0].split('_')[2]
                res_dict['Structures_info'][label]['coulombic_energy'] = enrg

        for s in output_list:
            if s[-3:] == 'cif':
                sp = s.split('_')
                label = sp[2]
                degneracy = sp[-1].split('.')[0][1:]

                s_content = self.retrieved.get_object_content(f'Output/{s}')
                s_pmg = Structure.from_str(s_content, fmt='cif')
                s_pmg.sort()

                spg = SpacegroupAnalyzer(s_pmg)
                res_dict['Structures_info'][label]['degeneracy'] = int(degneracy)
                res_dict['Structures_info'][label]['crystal_system'] = spg.get_crystal_system()
                res_dict['Structures_info'][label]['lattice_type'] = spg.get_lattice_type()
                res_dict['Structures_info'][label]['space_group_symbol'] = spg.get_space_group_symbol()

                s_dict[label] = StructureData(pymatgen_structure=s_pmg)

        result_dict.update(res_dict)

        self.out('output_parameters', Dict(dict=result_dict))
        for key, value in s_dict.items():
            self.out(f'output_structures.{key}', value)
        return None


#EOF
