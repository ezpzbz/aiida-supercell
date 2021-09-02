===============================
How to provide input parameters
===============================

All available input parameters are given below this page. They have minimal self-explanatory help
and I recommend consulting the ``Supercell`` manual and tutorial to get further insight. Herein, I 
provide general information on how to set up input paramters for plugin. 


Constructing ``builder``
========================
By having following lines in your submission script, you can get an input builder where you can assign each input:

.. code-block:: python

    from aiida.plugins import CalculationFactory

    SupercellCalculation = CalculationFactory('supercell')
    builder = SupercellCalculation.get_builder()


Then, each of inputs listed below, can be assigned to the ``builder``. For example, the following snippet 
will set the ``calculate`` to ``True`` which results in calculation of electrostatic energies:

.. code-block:: python

    from aiida import orm

    builder.calculate_coulomb_energies = orm.Bool(True)

Or the following snippet, will create a ``SinglefileData`` and then will provide it to ``builder``
as ``structure``:

.. code-block:: python
    
    from aiida.orm import DataFactory
    
    SinglefileData = DataFactory('singlefile')
    singlefileobject = SinglefileData(file=absolute_path/to/CIF)
    builder.structure = singlefileobject


**Note** Objects which are being assigned to ``builder`` has to be ``AiiDA`` data objects. 

Below I provide a little bit of more explanation on few special input parameters:

charges
+++++++
In case you want to provide the charges explicitly in run time (for example, giving structure as ``StructureData``,
or wanting to do the calculations with different set of charges), you can provide them as a ``Dict`` via ``charges``
input parameter. Herein, you may provide charge for each atom label available in the structure (if they are defined in
``StructureData``), or you may use wildcards.

.. code-block:: python

    from aiida import orm

    builder.charges = orm.Dict(dict={'Ca*': 2, 'Al*': 3, 'Si*': 4, 'O*': -2})

The above input will set the charges on all ``Ca`` sites to ``2`` and so on so forth. 

random_seed
+++++++++++
Usually you do not need to set this parameter. ``Supercell`` generates and use it during the run time. However, 
``aiida-supercell`` parses and stores the used ``random_seed`` in ``output_parameters``. It can be used for 
reproducing the results. 

sample_structures
+++++++++++++++++
``Supercell`` is very powerful in enumerating and sampling huge configuration spaces. Using the ``sample_structures``
input parameters, we can control how to sample structures for further calculations. We provide this input as 
``Dict`` which accepts following keys:

* **random**: number of structures to be sampled randomly.
* **low_energy**: number of structures with lowest electrostatic energy to be sampled. 
* **high_energy**: number of structures with highest electrostatic energy to be sampled. 
* **first**: number of structures to be sampled from the beginning of enumeration
* **last**: number of structures to be sampled from the end of enumeration
* **degeneracy**: number of structures to be sample with the degenracy equal or smaller than the value. 

For example, 

.. code-block:: python

    builder.sample_structures = Dict(dict={
        'low_energy': 2,
        'high_energy': 2,
        'random': 2,
    })

save_as_archive
+++++++++++++++
In disordered materials, we often face cases where the number of resulting structures after enumeration are in the order
of thousands, millions, and even billions. Therefore, it is not feasible to store all of them seperately. In these case,
we can set the ``save_as_archive`` to ``True``. All structures will be stored but in a single file named
``aiida_supercell.tar.gz`` and will be retrieved to the repository. 

Available inputs and outputs
++++++++++++++++++++++++++++

.. aiida-calcjob:: SupercellCalculation
    :module: aiida_supercell.calculations