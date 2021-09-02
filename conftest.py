"""
For pytest initialise a test database and profile
"""
import os
import pytest

pytest_plugins = ['aiida.manage.tests.pytest_fixtures']  # pylint: disable=invalid-name

thisdir = os.path.dirname(os.path.realpath(__file__))  # pylint: disable=invalid-name
# prepend_text = 'source ' + str(os.path.join(thisdir, '.github', 'setup.sh'))  # pylint: disable=invalid-name


@pytest.fixture(scope='function')
def code(aiida_local_code_factory):  # pylint: disable=unused-argument
    return aiida_local_code_factory(entry_point='supercell', executable='supercell')


#EOF
