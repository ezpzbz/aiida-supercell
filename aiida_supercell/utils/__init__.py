"""Parser function for Supercell outputs"""

from collections import defaultdict


def parse_supercell_output(output_string: str) -> dict:  #pylint: disable=too-many-branches
    """Parses output of supercell `output.log` file

    Args:
        output_string (str): Content of OUTPUT.log as string
    Returns:
        dict: Dictionary of parsed and selected results.
    """
    group_counter = 0
    lines = output_string.splitlines()

    output_dict = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(dict))))
    for line in lines:
        if 'Random SEED:' in line:
            rs = int(line.split()[-1])
            output_dict['Random_seed'] = rs
        if 'Chemical Formula' in line:
            output_dict['Chemical_formula']['Initial'] = ''.join(line.split()[2:])
        if 'Chemical formula of the supercell' in line:
            output_dict['Chemical_formula']['Supercell'] = ''.join(line.split()[5:])

        if 'Total charge of supercell' in line:
            chg = int(line.split()[-1])
            output_dict['Supecell_total_charge'] = chg
            if chg != 0:
                output_dict['WARNING'] = 'Supercell is NOT charge balanced!'

        if 'The total number of combinations is' in line:
            num = line.split()[-1]
            if '(' in num:
                output_dict['Number_of_structures']['total_combinations'] = int(line.split()[-1].split('(')[0])
            else:
                output_dict['Number_of_structures']['total_combinations'] = int(line.split()[-1])
        if 'symmetry operation found for supercell' in line:
            output_dict['Number_of_symmetry_operations'] = int(line.split()[0])
        if 'Combinations after merge' in line:
            output_dict['Number_of_structures']['symmetrically_distinct'] = int(line.split()[-1])

        if 'Site' in line:
            sp = line.split()
            if sp[2] == '#1:':
                group_counter += 1
            site = sp[2][1]
            output_dict['Crystallographic_groups'][f'Group{group_counter}'][f'Site{site}']['Symbol'] = sp[3]
            output_dict['Crystallographic_groups'][f'Group{group_counter}'][f'Site{site}']['Type'] = sp[7]
            if sp[7] == 'distributed':
                d = {}
                d['considered_sites'] = sp[9]
                d['total_sites'] = sp[13]
                output_dict['Crystallographic_groups'][f'Group{group_counter}'][f'Site{site}'].update({
                    'Type': {
                        'distributed': d
                    }
                })

            output_dict['Crystallographic_groups'][f'Group{group_counter}'][f'Site{site}']['Initial_occupancy'] = float(
                sp[5].strip(')')
            )
            output_dict['Crystallographic_groups'][f'Group{group_counter}'][f'Site{site}']['Actual_occupancy'] = float(
                sp[-1][:-1].strip(')')
            )

    return output_dict


#EOF
