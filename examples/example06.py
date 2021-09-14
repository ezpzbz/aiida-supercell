"""Example for Supercell and Magnetic Enumeration"""
import os
import sys
import click

from pymatgen.core import Structure

from aiida.common import NotExistent
from aiida.engine import run_get_pk
from aiida.plugins import WorkflowFactory
from aiida import orm


def example_05(code: orm.Code):
    """Prepare the builder to submit.

    Args:
        code (Code): Supercell code object.
    """

    pwd = os.path.dirname(os.path.realpath(__file__))
    strc_pmg = Structure.from_file(os.path.join(pwd, 'LiFePO4_partial.cif'))
    structure = orm.StructureData(pymatgen_structure=strc_pmg)

    MagneticWorkChain = WorkflowFactory('magnetic')

    builder = MagneticWorkChain.get_builder()

    #supercell inputs
    builder.supercell.code = code
    builder.supercell.charges = orm.Dict(dict={'Li*': 1, 'Fe*': 2, 'P*': 5, 'O*': -2})
    builder.supercell.calculate_coulomb_energies = orm.Bool(True)
    builder.supercell.charge_balance_method = orm.Str('yes')
    builder.supercell.merge_symmetric = orm.Bool('True')
    builder.supercell.supercell_size = orm.List(list=[1, 1, 2])
    builder.supercell.save_as_archive = orm.Bool(False)
    builder.supercell.metadata.options.resources = {  #pylint: disable = no-member
        'num_machines': 1,
        'num_mpiprocs_per_machine': 1,
    }
    builder.supercell.metadata.options.max_wallclock_seconds = 1 * 30 * 60

    #Workchain inputs
    builder.structure = structure
    builder.selection_criteria = orm.Str('low_energy')
    builder.default_magmoms = orm.Dict(dict={'Li': 0, 'Fe': 5, 'P': 0, 'O': 0})
    builder.strategies = orm.List(list=['ferromagnetic', 'antiferromagnetic'])

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
    example_05(code)


if __name__ == '__main__':
    cli()  # pylint: disable=no-value-for-parameter

# EOF
