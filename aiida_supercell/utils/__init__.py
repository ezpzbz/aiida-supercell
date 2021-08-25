"""Parser function for Supercell outputs"""
from collections import defaultdict


def parse_supercell_output(output_string: str) -> dict:
    """Parses output of supercell output.log file
    Args:
        output_string (str): Content of OUTPUT.log as string
    Returns:
        dict: Dictionary of parsed and selected results.
    """
    lines = output_string.splitlines()

    output_dict = defaultdict(dict)

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

    return output_dict


#EOF
