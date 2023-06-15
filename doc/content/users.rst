.. _user:

**********
User guide
**********

.. only:: html

   .. topic:: Abstract

      The following section describes setup process and the command line interface
      of the package. Installing the required Python dependencies and the package
      itself will require no longer than 5 minutes.
      In order to run this package, Python>=3.9 is required.


Package setup
=============
The package installation, along with its requirements, requires no longer than
a few minutes. First of all, after downloading the package, it is necessary to
run the following command to install its Python dependencies:

.. code-block:: shell

   $ pip install -r requirements.txt

This command will automatically install all the required dependencies.
Currently, the only required Python packages are `Numpy <http://www.numpy.org/>`__
and `Scipy <https://www.scipy.org/>`__.

After the requirements have been installed, it is time to install the package
itself. In order to do so, execute the following command inside the repository
main directory:

.. code-block:: shell

   $ python setup.py install

This command will install all the simulator libraries and scripts into the
current Python environment, and they will be immediately available for
execution.


Run the simulators
==================
All the simulators can be run at once, by simply executing the following
command:

.. code-block:: bash

   $ discos-simulator start

To stop all the simulators at once:

.. code-block:: bash

   $ discos-simulator stop

By adding the ``--system`` or ``--s`` flag to the command, it is possible to
run a single simulator:

.. code-block:: bash

   $ discos-simulator start --system active_surface
   $ discos-simulator start -s acu

To stop the desired simulator:

.. code-block:: bash

   $ discos-simulator stop -s active_surface

.. _multi:

To run a specific configuration for a simulators, add the ``--type`` flag,
followed by the desired configuration:

.. code-block:: bash

    $ discos-simulator --system if_distributor --type IFD start

Not all simulators have multiple configurations. Providing an unknown
configuration will prevent the system from starting and the command will
fail.

To know the currently available simulators, execute the command using the
the ``list`` action:

.. code-block:: bash

   $ discos-simulator list
   Available simulators: 'active_surface', 'acu', 'backend', 'calmux', 'dbesm', 'if_distributor', 'lo', 'mscu', 'weather_station'.
