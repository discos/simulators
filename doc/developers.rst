.. _developer:

************************
Developers documentation
************************

.. topic:: Preface

   If you want to know how to write a brand new simulator, we advise you to
   read this section. You will also find some useful information in order to
   run some tests and how to contribute to this project. If you only want to
   know how to run a simulator, you can skip this section and head directly to
   the :ref:`user` chapter instead.


How to implement a simulator
============================
To implement a simulator, you need to create a module that
defines both a ``System`` class and a ``servers`` list.  The next
sections will describe the API of these two objects.
If you want to see an example, have a look at the
:download:`acu <../simulators/acu/__init__.py>` module.

The ``System`` class
--------------------
The ``System`` class must inherit from ``ListeningSystem``
or ``SendingSystem``, which are defined in
:download:`common.py <../simulators/common.py>`. Both of these classes
inherit from the ``BaseSystem`` class, also defined in ``common.py``.
A more complex ``System`` class can inherit from both ``ListeningSystem``
and ``SendingSystem``, behaving simultaneously as the two of them.

The ``ListeningSystem`` class and the ``System.parse()`` method
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If the ``System`` class inherits from ``common.ListeningSystem``, it must define
the ``parse()`` method::

    from simulators.common import ListeningSystem


    class System(ListeningSystem):

        def parse(self, byte):
            ...

The ``System.parse()`` interface is described in `issue #1
<https://github.com/discos/simulators/issues/1>`__. in the GitHub repository.
This method takes one byte (string of one character, in Python 2) as argument
and returns:

* ``False`` when the byte is not recognized as a message header and the system is
  still waiting for the correct header character
* ``True`` when the system has already received the header and it is waiting to
  receive the rest of the message
* a response to the client, a non empty string, built according to the protocol
  definition. The syntax of the response thus is different between different
  simulators.

If the system has nothing to send to the client, as in the case of broadcast
requests, ``System.parse()`` must return ``True``.
When the simulator is lead to behave unexpectedly, a ``ValueError`` has to be
raised, it will be captured and logged by the parent server process.

The ``SendingSystem`` class and the ``System.subscribe()`` and ``System.unsubscribe()`` methods
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If the ``System`` class inherits from ``common.SendingSystem``, it has to define and implement
the ``subscribe()`` and ``unsubscribe()`` methods, along with the ``sampling_time`` attribute::

    from simulators.common import SendingSystem


    class System(SendingSystem):

        self.sampling_time = ... [ms]

        def subscribe(self, q):
            ...

        def unsubscribe(self, q):
            ...

The ``System.subscribe()`` interface is described in `issue #175
<https://github.com/discos/simulators/issues/175>`__ on GitHub. This method
takes a queue object as argument and adds it to the list of the connected
clients. For each client in this list the system will then be able to send
the required message by putting it into each of the clients queues.

The ``System.unsubscribe()`` interface is also described in `issue #175
<https://github.com/discos/simulators/issues/175>`__ on GitHub. This method
receives once again the same queue object received by the ``System.subscribe()``
method, letting the system know that that queue object, relative to a
disconnecting client, had to be removed from the clients queues.

The ``sampling_time`` attribute defines the time period (in milliseconds)
that elapses between two consecutive messages that the system have to send
to its clients. It is internally defined in the ``SendingSystem`` base class,
and its default value is equal to 10ms. If a different sampling time is needed,
it is sufficient to override this variable in the inheriting ``System`` class.

Inheriting from both ``ListeningSystem`` and ``SendingSystem``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A ``System`` class can inherit from both ``ListeningSystem`` and ``SendingSystem`` at
the same time. If it does, it must implement the ``System.parse()``, the
``System.subscribe()`` and the ``System.unsubscribe()`` methods, along with
defining the ``sampling_time`` attribute.

The ``servers`` list
--------------------

The ``servers`` list defines all the instances that should be running when the
given simulator starts. Each element of the ``servers`` list is a tuple,
composed of the following items:

* the server listening address, ``l_address``
* the server sending address, ``s_address``
* the type of threading server from the ``SocketServer`` package to use to run
  the simulator
* a dictionary of optional keyword arguments, ``kwargs``, eventually used by
  ``System.__init__()``

The ``l_address`` item is the address on which the server will listen for incoming
commands to pass down to the ``System.parse()`` method. The ``s_address`` item
is the address from which the server will periodically send its data to its connected
clients. The type of threading server from the ``SocketServer`` argument can be either
``ThreadingTCPServer`` or ``ThreadingUDPServer``, depending on the type of socket the
server has to use. These Python object types have to be imported as follows::

    from SocketServer import ThreadingTCPServer

or::

    from SocketServer import ThreadingUDPServer

Some ``servers`` list examples
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Let us suppose the system we have to simulate has 2 listening TCP servers and no
sending servers, the first one with address ``('192.168.100.10', 5000)`` and the
second one with address ``('192.168.100.10', 5001)``.  In that case we have to
define the ``servers`` list as follows::

    servers = [
        (('192.168.100.10', 5000), (), ThreadingTCPServer, {}),
        (('192.168.100.10', 5001), (), ThreadingTCPServer, {}),
    ]

If our ``System`` class takes some extra arguments, two integers, for instance,
we have to pass them via the ``kwargs`` dictionary.  For instance::

    servers = [
        (('192.168.100.10', 5000), (), ThreadingTCPServer, {'arg1': 10, 'arg2': 20}),
        (('192.168.100.10', 5001), (), ThreadingTCPServer, {'arg1': 4, 'arg2': 5}),
    ]

If the system we want to simulate has instead a single listening UDP server, we
have to define the ``servers`` list as follows::

    servers = [
        (('192.168.100.10', 5000), (), ThreadingUDPServer, {}),
    ]

If the system we want to simulate has instead 3 sending TCP servers and no
listening servers, the ``servers`` list should be defined as follows::

    servers = [
        ((), ('192.168.100.10', 5002), ThreadingTCPServer, {}),
        ((), ('192.168.100.10', 5003), ThreadingTCPServer, {}),
        ((), ('192.168.100.11', 5000), ThreadingTCPServer, {}),
    ]

Finally, a system instance can act as both listening and sending server. In this case,
each server list entry must be defined as follows::

    servers = [
        (('192.168.100.10', 5003), ('192.168.100.10', 5004), ThreadingTCPServer, {}),
        (('192.168.100.10', 6000), ('192.168.100.10', 6001), ThreadingTCPServer, {}),
    ]

If you want to see another example, take a look at the
:download:`active surface <../simulators/active_surface/__init__.py>` module.
The active surface system is composed of 96 listening TCP servers, and in fact
its ``servers`` list in defined in the following way::

    servers = []
    for line in range(96):                              # 96 servers
        l_address = ('0.0.0.0', 11000 + line)           # Compose the address
        servers.append((
            l_address,
            (),                                         # No sending servers
            ThreadingTCPServer,                         # TCP connection
            {'min_usd_index': 1, 'max_usd_index': 17}   # Some extra args
        ))

The ``MultiTypeSystem`` class
-----------------------------

Some simulators might have multiple different implementations, having therefore
multiple ``System`` classes that behave differently from one another. In order
to keep different ``System`` classes under the same simulator name, we wrote
another class, called ``MultiTypeSystem``, that acts as a ``class factory``.
It works by receiving the name of the configuration of the system we want to
launch as ``system_type`` keyword argument. The class is defined in
:download:`common.py <../simulators/common.py>`, as follows::

    class MultiTypeSystem(object):

        def __new__(self, **kwargs):
            if cls.system_type not in cls.systems:
                raise ValueError(...)

            return cls.systems[cls.system_type].System(**kwargs)

The main ``System`` class,. just like a regular ``System`` class, should be
defined in the ``__init__.py`` file, inside the module main directory. It must
inherit from the ``MultiTypeSystem`` class and override the ``__new__`` method
as shown below::

    systems = get_multitype_systems(__file__)

    class System(MultiTypeSystem):

        def __new__(cls, **kwargs):
            cls.systems = systems
            cls.system_type = kwargs.pop('system_type')
            return MultiTypeSystem.__new__(cls, **kwargs)

As you can see from the code above, before defining the class, we need to
retrieve the list of the available configurations for the given simulator. It
can be done by calling the ``get_multitype_systems`` function, defined in the
``utils`` library. The said function will recursively search for any ``System``
class in the given path. In general, the passed ``__file__`` value will ensure
that only the ``System`` classes defined in the module's directory and
sub-directories, will end up inside the ``systems`` list. For more
information about the ``get_multitype_systems`` function, take a look at the
:ref:`function<get_multitype_systems>` in the :ref:`api` section.
The default system configuration can be defined as ``system_type`` inside the
``servers`` list ``kwargs`` dictionary. It can be done in the following way::

    servers = [
        (('0.0.0.0', 12000), (), ThreadingTCPServer, {'system_type': '...'})
    ]

In order to select the desired system configuration via the command line, just
pass the ``-t``, or ``--type`` argument when launching the simulator::

    discos-simulator -s if_distributor -t IFD start

or::

    discos-simulator -s if_distributor -t IFD_14_channels start


Custom commands
---------------

Custom commands are useful for several use cases. For instance,
suppose we want the simulator to reproduce some error conditions
by changing the ``System`` state. We just need to define a method that
starts with ``system_`` inside our ``System`` class. I.e::

    class System(BaseSystem):

        def system_generate_error_x(self):
            # Change the state of the System
            ...

After implementing this method, the clients are able to call it
by sending the custom command ``$system_generate_error_x!``.  We can
also define methods with parameters. In this case the custom
command will be in the form ``$system_commandname:par1,par2,par3!``.

To avoid name clashing, do not head other methods with ``system_``,
so use this convention only for custom commands.


Useful functions
----------------

In order to make it faster to write and implement new simulator's methods,
which sometimes require converting data from a format to another, a library of
useful functions called ``Utils`` has been written and comes within the simulators
package. Its API is described in the :ref:`api` section.


Testing environment
===================
In the continuous deployment workflow, the tests are executed more than
once.  During development you will execute the tests locally, and
after pushing your code to Github, the tests will be executed on
`Travis-CI <https://travis-ci.org/>`__.


Dependencies
------------
To :ref:`unit-tests` you do not need to install any additional depencency.
That is possible thanks to the ``unittest`` framework, included in the
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
   $ pip install tox
   $ sudo apt install ruby          # apt, yum, ...
   $ sudo gem install wwtd          # run travis-ci locally


Run all tests at once
---------------------
You can run all tests by executing this single command:

.. code-block:: shell

   $ wwtd

The ``wwtd`` program (``What Would Travis Do``) reads the *.travis.yml*
file and executes the tests accordingly.  You can also run the tests
manually, one by one, as described in the following sections.

Run the linter
--------------
If you do not know what a linter is, please take 10 minutes to read the
`Wikipedia definition <https://en.wikipedia.org/wiki/Lint_(software)>`__.
To run the linter move to the project's root directory and execute the
following command:

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
If you want to see the percentage of code covered by test,
run the unit tests using `Coverage.py
<https://coverage.readthedocs.io/>`__:

.. code-block:: shell

   $ coverage run -m unittest discover -b tests

Now you can generate an HTML report:

.. code-block:: shell

   $ coverage combine && coverage report && coverage html

To see the HTML report open the generated *htmlcov/index.html*
file with your browser.


Test the documentation
----------------------
We want to test different things:

* the docstring examples
* the documentation (*doc* directory) examples
* the links inside the documentation must point correctly to the target
* the HTML must be generated properly

To test the docstring examples, we use the Python standard library
``doctest`` module. Simply move to the
project's root directory and execute the following command:

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
