===============
Getting started
===============

Prerequisite
============

AiiDA
+++++
We assume that you have a working installation of ``AiiDA``. As we require ``pymatgen`` for part of 
symmetry analysis, you need to install ``AiiDA`` by:

.. code-block:: bash

    pip install aiida-core .[atomic_tools]

Supercell
+++++++++
``Supercell`` program needs to be downloaded or compiled. Then, you need to setup the ``code`` in ``AiiDA``.
You may consult ``AiiDA`` documentation for further information. 


``aiida-supercell`` Installation
================================
Currently, you may install the plugin by:

.. code-block:: bash

    git clone https://github.com/pzarabadip/aiida-supercell .
    pip install .

**Note** It will be deployed to ``pypi`` for easier installation. 

