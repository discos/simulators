.. _user:

*******************
Users documentation
*******************

.. topic:: Preface

   If you want to know how to use the simulators
   in order to run your code without the real hardware, then you
   have to read this section.  If you instead want to know how to
   write a simulator, how to run the tests or how to contribute to
   this project, then you have to read the :ref:`developer` chapter.
   This project requires Python 2.7.


Run the simulators
==================
To run a simulator use the ``discos-simulator`` command.  For instance, to
run the active surface simulator:

.. code-block:: bash

   $ discos-simulator start --system active_surface

You can also use the ``-s`` shortcut:

.. code-block:: bash

   $ discos-simulator start -s active_surface

To stop the simulator:

.. code-block:: bash

   $ discos-simulator stop -s active_surface

To run a specific configuration for some of the simulators:

.. code-block:: bash

    $ discos-simulator --system if_distributor --type IFD start

The ``--type`` flag, or its shortcut ``-t``, will let you specify a
configuration for the desired simulator. Not all simulators have multiple
configurations. Providing an unknown configuration will prevent the system
from starting and the operation will fail.

Currently available simulators are: ``active_surface``, ``acu`` and
``if_distributor`` with configurations ``IFD`` and ``IFD_14_channels``.
