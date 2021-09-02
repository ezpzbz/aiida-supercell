=======================
How to setup structures
=======================

There are two ways to feed your initial structure to `aiida-supercell`, i.e. CIF as `SinglefileData`
and structure stored as `StructureData` object. Below, you can find cons and pros for each of options.


CIF
===
We normally access to the structure of disordered solids via CIF where partial occupancy of each site
is provided. It also can contain the formal charges for each site. The most straightfoward way to 
use `aiida-supercell` is storing the CIF as ``SinglefileData`` and then use it for the calculations:

.. code-block:: python
    
    from aiida.orm import DataFactory
    SinglefileData = DataFactory('singlefile')
    singlefileobject = SinglefileData(file=absolute_path/to/CIF)

If this step is done detached from submission script, the created `AiiDA` object needs to stored and 
the `pk` or `uuid` needs to be recorded for actual calculations:

.. code-block:: bash

    <SinglefileData: uuid: 10419a5f-dd70-4659-bb13-e33544d2724f (unstored)>

.. code-block:: python

    singlefileobject = SinglefileData(path=path/to/CIF).store()

Providing formal charges
++++++++++++++++++++++++
In case you would like to provide the formal charges within the ``CIF``, charges are needed to be defined as:

.. code-block:: bash

    loop_
    _atom_type_symbol
    _atom_type_oxidation_number
    Ca1  +2
    AlT1 +3
    AlT2 +3
    SiT2 +4
    O1   -2
    O2   -2
    O3   -2

while ``_atom_type_symbol`` has to be same as ``_atom_site_label`` as below:

.. code-block:: bash

    loop_
    _atom_site_label
    _atom_site_fract_x
    _atom_site_fract_y
    _atom_site_fract_z
    _atom_site_occupancy
    Ca1   0.33750 0.16250 0.51100 1.00000
    AlT1  0.00000 0.00000 0.00000 1.00000
    AlT2  0.14310 0.35690 0.95280 0.50000
    SiT2  0.14310 0.35690 0.95280 0.50000
    O1    0.50000 0.00000 0.18840 1.00000
    O2    0.14180 0.35820 0.28320 1.00000
    O3    0.08720 0.17060 0.80330 1.00000

StructureData
=============
The other way to provide structure, is reading the structure and then storing it as `StructureData`. It needs to
be carefully checked by user whether the partial occupancies are read and written correctly. 

.. code-block:: python

    from pymatgen.core import Structure
    from aiida.orm import DataFactory

    StructureData = DataFactory('structure')
    strc_pmg = Structure.from_file('path/to/CIF')
    structure = StructureData(pymatgen_structure=strc_pmg)


Providing formal charges
++++++++++++++++++++++++
In this case, providing formal charges should be done through ``charges`` input parameter.
