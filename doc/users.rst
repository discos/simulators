.. _user:

*******************
Users documentation
*******************

.. topic:: Preface

   If you want to know how to use the simulators in order to run your code
   without having to rely on the hardware, then you can find all the
   information you need in this section.


Run the simulators
==================
You can run all the simulators at once, by simply executing the following
command:

.. code-block:: bash

   $ discos-simulator start

To stop all the simulators at once:

.. code-block:: bash

   $ discos-simulator stop

You can also run a single simulator by adding the ``--system`` flag to the
command:

.. code-block:: bash

   $ discos-simulator start --system active_surface

You can also use the ``-s`` shortcut:

.. code-block:: bash

   $ discos-simulator start -s active_surface

To stop the desired simulator:

.. code-block:: bash

   $ discos-simulator stop -s active_surface

To run a specific configuration for a simulators, you have to add the
``--type`` flag, followed by the desired configuration:

.. code-block:: bash

    $ discos-simulator --system if_distributor --type IFD start

Not all simulators have multiple configurations. Providing an unknown
configuration will prevent the system from starting and the command will
fail.

To know the currently available simulators, you can execute the command using
the ``list`` action:

.. code-block:: bash

   $ discos-simulator list
   Available simulators: 'active_surface', 'acu', 'backend', 'calmux', 'if_distributor', 'lo', 'mscu', 'weather_station'.
