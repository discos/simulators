.. _developer:

************************
Developers documentation
************************

.. only:: html

   .. topic:: Abstract

      If you want to know how to write a brand new simulator, we advise you to
      read this section. You will also find some useful information in order to
      run some tests and how to contribute to this project. If you only want to
      know how to run a simulator, you can skip this section and head directly to
      the :ref:`user` chapter instead.


How to implement a simulator
============================
To implement a simulator, it is necessary to create a module that defines both
a `servers` list and a `System` class.

The `servers` list
------------------
The `servers` list defines all the instances that should be running when the
given simulator starts. Each element of the `servers` list is a tuple, composed
of the following items:

* the server listening address, `l_address`
* the server sending address, `s_address`
* the type of threading server from the `SocketServer` package to use to run
  the simulator
* a dictionary of optional keyword arguments, `kwargs`, eventually used by
  `System.__init__()`

The `l_address` item is the address on which the server will listen for
incoming commands to pass down to the `System.parse()` method. The `s_address`
item is the address from which the server will periodically send its data to
its connected clients. The type of threading server from the `SocketServer`
argument can either be `ThreadingTCPServer` or `ThreadingUDPServer`, depending
on the type of socket the server has to use.
These Python object types have to be imported as follows::

    from SocketServer import ThreadingTCPServer

or::

    from SocketServer import ThreadingUDPServer

Some examples
~~~~~~~~~~~~~
Suppose the reader wants to simulate a system that has 2 listening TCP servers
and no sending servers, the first one with address ``('192.168.100.10', 5000)``
and the second one with address ``('192.168.100.10', 5001)``. In this case we
have to define the `servers` list as follows::

    servers = [
        (('192.168.100.10', 5000), (), ThreadingTCPServer, {}),
        (('192.168.100.10', 5001), (), ThreadingTCPServer, {}),
    ]

If the `System` class accepts some extra arguments, two integers, for instance,
it is possible to pass them via the `kwargs` dictionary::

    servers = [
        (('192.168.100.10', 5000), (), ThreadingTCPServer, {'arg1': 10, 'arg2': 20}),
        (('192.168.100.10', 5001), (), ThreadingTCPServer, {'arg1': 4, 'arg2': 5}),
    ]

If the `System` to simulate has instead a single listening UDP server, the
`servers` list will be defined as follows::

    servers = [
        (('192.168.100.10', 5000), (), ThreadingUDPServer, {}),
    ]

A `System` with 3 sending TCP servers and no listening servers will have the
`servers` list defined in the following way::

    servers = [
        ((), ('192.168.100.10', 5002), ThreadingTCPServer, {}),
        ((), ('192.168.100.10', 5003), ThreadingTCPServer, {}),
        ((), ('192.168.100.11', 5000), ThreadingTCPServer, {}),
    ]

Finally, a system instance can act as both listening and sending server.
In this case, each server list entry must be defined as follows::

    servers = [
        (('192.168.100.10', 5003), ('192.168.100.10', 5004), ThreadingTCPServer, {}),
        (('192.168.100.10', 6000), ('192.168.100.10', 6001), ThreadingTCPServer, {}),
    ]

Be aware that multiple lines in the `servers` list will cause the simulator to
spawn a `System` object per line. Every one of the spawned `System` objects is
independent from the others and they will all act as different simulators.


Custom commands
---------------
Custom commands are useful for several use cases. For instance, suppose we want
the simulator to reproduce some error conditions by changing the `System`
state. We just need to define a method that starts with `system_` inside the
`System` class. I.e::

    class System(ListeningSystem):

        def system_generate_error_x(self):
            # Change the state of the System
            ...

After implementing this method, the clients are able to call it by sending the
custom command `$system_generate_error_x%`. It is also possible to define a
method that accepts some parameters. In this case the custom command will have
the form `$system_commandname:par1,par2,par3%`. Since every `Server` object is
not limited to only a single connection, custom commands can be also sent by a
different client that the main one. This allow the reproduction of error
scenarios even when the `DISCOS` control software is already connected to some
simulator.

In order to avoid name clashing for custom methods, it is sufficient to not
use the `system_` prefix for any other `System` method, so make sure to only
use this convention for custom commands.


Useful functions
----------------
In order to make it faster to write and implement new simulator's methods,
which sometimes require converting data from a format to another, a library of
useful functions called `simulators.utils` has been written and comes within
the simulators package. Its API is described in the :ref:`utils` section.


Testing environment
===================
In the `continuous integration` workflow, the tests are executed more than
once.  During the development process, tests will be executed locally, and
after pushing the code to Github, they will be executed on
`Travis-CI <https://travis-ci.org/github/discos/simulators>`__.


Dependencies
------------
To :ref:`unit-tests` there is no need to install any additional depencency.
That is possible thanks to the `unittest` framework, included in the
Python standard library. But we do not want to only run the unit tests:
we want to set up an environment that allows us to check for suspicious
code, test the code and the documentation, evaluate the testing coverage,
and replicate the Travis-CI build locally.  To accomplish this goal we
need to install some additional dependencies:

.. code-block:: shell

   $ pip install coverage           # testing coverage tool
   $ pip install codecov            # testing coverage tool
   $ pip install coveralls          # testing coverage tool
   $ pip install prospector         # Python linter
   $ pip install sphinx             # documentation generator
   $ pip install sphinx_rtd_theme   # HTML doc theme
   $ pip install tox                # testing tool
   $ sudo apt install ruby          # apt, yum, ...
   $ sudo gem install wwtd          # run travis-ci locally


Run all tests at once
---------------------
All tests can be run at once by executing this single command:

.. code-block:: shell

   $ wwtd

The `wwtd` program (`What Would Travis Do`) reads the *.travis.yml*
file and executes the tests accordingly. The tests can also be run
manually, one by one, as described in the following sections.

Run the linter
--------------
To run the `linter <https://en.wikipedia.org/wiki/Lint_(software)>`__ move to
the project's root directory and execute the following command:

.. code-block:: shell

   $ prospector


.. _unit-tests:

Run the unit tests
------------------
Move to the project's root directory and execute the following command:

.. code-block:: shell

   $ python -m unittest discover -b tests


Check the testing coverage
--------------------------
To check the percentage of code covered by test, run the unit tests using
`Coverage.py <https://coverage.readthedocs.io/>`__:

.. code-block:: shell

   $ coverage run -m unittest discover -b tests

Now generate an HTML report:

.. code-block:: shell

   $ coverage combine && coverage report && coverage html

To see the HTML report open the generated *htmlcov/index.html*
file with your browser.


Test the documentation
----------------------
Several things have to be tested:

* the docstring examples
* the documentation (*doc* directory) examples
* the links inside the documentation must point correctly to the target
* the HTML must be generated properly

To test the docstring examples, we use the Python standard library `doctest`
module. Simply move to the root directory of the project and execute the
following command:

.. code-block:: shell

   $ python -m doctest simulators/*.py

To test the examples in the *doc* directory:

.. code-block:: shell

   $ cd doc
   $ make doctest

To check if there are broken URLs in the documentation:

.. code-block:: shell

   $ make linkcheck  # From the doc directory

To generate the HTML:

.. code-block:: shell

   $ make html  # From the doc directory
