=====================================
Output parameters
=====================================

``aiida-supercell`` parses the output log of ``Supercell`` and stores (almost) all data in ``output_parameters``
``Dict``. 

.. figure:: /images/output_parameters.png
    :height: 20cm

    A sample represenation of ``output_parameters``.

|

We use ``pymatgen`` to analyze the space group of each structure and these info are also stored in the dictionary.

**Note** Symmetry analysis is done only if we sample a handful of structures. In the case of ``save_as_archive``, it is
not being performed. 


