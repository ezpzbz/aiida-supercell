"""Example using StructureData"""
import os
import sys
import click

from pymatgen.core.structure import Structure

from aiida.common import NotExistent
from aiida.plugins import DataFactory
from aiida.engine import run_get_pk
from aiida.plugins import CalculationFactory
from aiida.orm import Code, Dict, Bool, Str, List

StructureData = DataFactory('structure')


def example_02(code: Code):
    """Prepare the builder to submit.

    Args:
        code (Code): Supercell code object.
    """

    pwd = os.path.dirname(os.path.realpath(__file__))
    strc = Structure.from_file(os.path.join(pwd, 'test.cif'))
    structure = StructureData(pymatgen_structure=strc)

    SupercellCalculation = CalculationFactory('supercell')

    builder = SupercellCalculation.get_builder()

    builder.code = code
    builder.structure = structure
    builder.charges = Dict(dict={'Ca*': 2, 'Al*': 3, 'Si*': 4, 'O*': -2})
    builder.calculate_coulomb_energies = Bool(True)
    builder.charge_balance_method = Str('yes')
    builder.merge_symmetric = Bool('True')
    builder.supercell_size = List(list=[1, 1, 2])
    builder.metadata.options.resources = {  #pylint: disable = no-member
        'num_machines': 1,
        'num_mpiprocs_per_machine': 1,
    }
    builder.save_as_archive = Bool(False)
    builder.metadata.options.max_wallclock_seconds = 1 * 30 * 60

    builder.sample_structures = Dict(
        dict={
            'low_energy': 2,
            'high_energy': 2,
            'random': 2,
            'first': 1,
            'last': 1,
            'degeneracy': 8
        }
    )

    _, pk = run_get_pk(builder)
    print('calculation pk: ', pk)


@click.command('cli')
@click.argument('codelabel')
def cli(codelabel):
    """Click interface"""
    try:
        code = Code.get_from_string(codelabel)
    except NotExistent:
        print("The code '{}' does not exist".format(codelabel))
        sys.exit(1)
    example_02(code)


if __name__ == '__main__':
    cli()  # pylint: disable=no-value-for-parameter

# EOF
