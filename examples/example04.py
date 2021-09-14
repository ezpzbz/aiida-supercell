"""Example using SinglefileData"""
import os
import sys
import click

from aiida.common import NotExistent
from aiida.engine import run_get_pk
from aiida.plugins import CalculationFactory
from aiida import orm


def example_04(code: orm.Code):
    """Prepare the builder to submit.

    Args:
        code (Code): Supercell code object.
    """

    pwd = os.path.dirname(os.path.realpath(__file__))
    structure = orm.SinglefileData(file=os.path.join(pwd, 'test.cif'))

    SupercellCalculation = CalculationFactory('supercell')

    builder = SupercellCalculation.get_builder()

    builder.code = code
    builder.structure = structure
    builder.charges = orm.Dict(dict={'Ca*': 2, 'Al*': 3, 'Si*': 4, 'O*': -2})
    builder.calculate_coulomb_energies = orm.Bool(True)
    builder.charge_balance_method = orm.Str('yes')
    builder.merge_symmetric = orm.Bool('True')
    builder.supercell_size = orm.List(list=[1, 1, 2])
    builder.metadata.options.resources = {  #pylint: disable = no-member
        'num_machines': 1,
        'num_mpiprocs_per_machine': 1,
    }
    builder.metadata.options.max_wallclock_seconds = 1 * 30 * 60

    builder.save_as_archive = orm.Bool(True)

    _, pk = run_get_pk(builder)
    print('calculation pk: ', pk)


@click.command('cli')
@click.argument('codelabel')
def cli(codelabel):
    """Click interface"""
    try:
        code = orm.Code.get_from_string(codelabel)
    except NotExistent:
        print("The code '{}' does not exist".format(codelabel))
        sys.exit(1)
    example_04(code)


if __name__ == '__main__':
    cli()  # pylint: disable=no-value-for-parameter

# EOF
