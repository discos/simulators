.. _developer:

************************
Developers documentation
************************

Testing environment
===================
In the contiunuos deployment workflow, the tests are executed more than
once.  During development you will execute the tests locally, and
after pushing your code to Github, the tests will be executed on
`Travis-CI <https://travis-ci.org/>`__.


Dependencies
------------
To :ref:`unit-tests` you do not need to install any depencency.
That is because we are using the ``unittest`` framework, included in the
Python standard library.  But we do not want to only run the unit tests:
we want to set up an environment that allows us to check for
suspicious code, test the code and the documentation, evaluate the testing
coverage, and replicate the Travis-CI build locally.  To accomplish this goal
we need some dependencies.  Let's install them:

.. code-block:: shell

   $ pip install coverage  # testing coverage tool
   $ pip install prospector  # linter
   $ pip install sphinx  # documentation generator
   $ pip install sphinx_rtd_theme  # HTML doc theme
   $ pip install tox
   $ sudo install ruby
   $ sudo gem install wwtd  # travis-ci locally


Run all tests at once
---------------------
You can run all tests by executing just one command:

.. code-block:: shell

   $ wwtd

The ``wwtd`` program reads the *travis.yml* file and executes
the tests accordingly.  You can also run the tests manually,
one by one, as described in the following sections.

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

   $ coverage combine
   $ coverage report
   $ coverage html

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
``doctest`` module.  If you do not know what we are
speaking about, than take 10 minutes to read this brief doctest `tutorial
<https://pymotw.com/2/doctest/>`__.  After that, move to the project's root
directory and execute the following command:

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


How to implement a simulator
============================
To implement a simulator, you need to create a module that
defines both a ``System`` class and a ``servers`` list.  The next
sections will exaplain the API of these two objects.
If you want to see an example, have a look at
:download:`acu <../simulators/acu/__init__.py>` module.

The ``System`` class
--------------------
The ``System`` class must inherit from ``ListeningSystem``
or ``SendingSystem``, which are defined in
:download:`common.py <../simulators/common.py>` and both
inherits from the ``BaseSystem`` class, also defined in ``common.py``.
A more complex ``System`` class can inherit from both ``ListeningSystem``
and ``SendingSystem``, behaving simultaneously as the two of them.

The ``ListeningSystem`` class and the ``System.parse()`` method
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If the ``System`` class inherits from ``server.ListeningSystem``, it has to define
a ``parse()`` method::

    from simulators.common import ListeningSystem


    class System(ListeningSystem):

        def parse(self, byte):
            ...

The ``System.parse()`` interface is described in `issue #1
<https://github.com/discos/simulators/issues/1>`__.  This method takes one byte
(string of one character, in Python 2) as argument and returns:

* ``False`` when the byte is not the message header and it is still waiting for the header
* ``True`` when it has already got the header and it is composing the message
* the reponse, a non empty string, when the system is half duplex and there is a response
  to be sent back to the client.

If the system has nothing to send to the client, as in the case of broadcast
requests, ``System.parse()`` has to return ``True``.
It eventually raises a ``ValueError`` in case there is an unexpected error (not
considered by the system protocol).

The ``SendingSystem`` class and the ``System.subscribe()`` and ``System.unsubscribe()`` methods
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If the ``System`` class inherits from ``server.SendingSystem``, it has to define
the ``subscribe()`` and ``unsubscribe()`` methods, along with a ``sampling_rate`` attribute::

    from simulators.common import SendingSystem


    class System(SendingSystem):

        self.sampling_rate = ...

        def subscribe(self, q):
            ...

        def unsubscribe(self, q):
            ...

The ``System.subscribe()`` interface is described in `issue #175
<https://github.com/discos/simulators/issues/175>`__.  This method takes a queue object
as argument and adds it to the list of the connected clients. For each client
in this list the system will then be able to send the required message putting
it into each of the clients queues.

The ``System.unsubscribe()`` interface is also described in `issue #175
<https://github.com/discos/simulators/issues/175>`__.  This method receives
once again the same queue object received by the ``System.subscribe()`` method,
letting the system know that that queue object, relative to a disconnecting
client, should be removed from the clients queues.

Inheriting from both ``ListeningSystem`` and ``SystemSystem``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A ``System`` class can inherit from both ``ListeningSystem`` and ``SendingSystem`` at
the same time. If it does, it has to implement the ``System.parse()``, the
``System.subscribe()`` and the ``System.unsubscribe()`` methods.


The ``servers`` list
--------------------

The elements of the ``servers`` list are tuples.  Each tuple is composed
of four items:

* the server listening address, ``l_address``
* the server sending address, ``s_address``
* the type of  threading server from the ``SocketServer`` package to use to run
  the simulator
* another tuple (let's call it ``args``) of possible arguments required
  by ``System.__init__()``.

Each element of the ``servers`` list represents an instance of the ``system``,
``l_address`` is the address in which the server will wait for its clients
to send the commands to pass to the ``System.parse()`` method. ``s_address`` is
the address from which the server will send its data received via the queue
registered to the system via the ``System.subscribe()`` method.
The type of threading server from the ``SocketServer`` argument can be either
``ThreadingTCPServer`` or ``ThreadingUDPServer``, depending on the type of
socket the server has to use. These Python object types have to be imported as
follows::

    from SocketServer import ThreadingTCPServer

or::

    from SocketServer import ThreadingUDPServer

Let's suppose the system to simulate has 2 listening TCP servers and no sending
servers, the first one with address ``('192.168.100.10', 5000)`` and the second
one with address ``('192.168.100.10', 5001)``.  In that case we have to define
the ``servers`` list as follows::

    servers = [
        ('192.168.100.10', 5000), (), ThreadingTCPServer, ()),
        ('192.168.100.10', 5001), (), ThreadingTCPServer, ()),
    ]

If our ``System`` class takes some extra arguments, let's say two integers,
we have to pass them throgh the ``args`` tuple.  For instance::

    servers = [
        ('192.168.100.10', 5000), (), ThreadingTCPServer, (10, 20)),
        ('192.168.100.10', 5001), (), ThreadingTCPServer, (4, 5)),
    ]

If the system we want to simulate has instead a single listening UDP server, we
have to define the ``servers`` list as follows::

    servers = [
        ('192.168.100.10', 5000), (), ThreadingUDPServer, ()),
    ]

If the system we want to simulate has instead 3 sending TCP servers and no
listening servers, we have to define the ``servers`` list as follows::

    servers = [
        ((), ('192.168.100.10', 5002), ThreadingTCPServer, ()),
        ((), ('192.168.100.10', 5003), ThreadingTCPServer, ()),
        ((), ('192.168.100.11', 5000), ThreadingTCPServer, ()),
    ]

Finally, a system instance can act as both listening and sending server. In this case,
each server list entry must be defined as follows::

    servers = [
        (('192.168.100.10', 5003), ('192.168.100.10', 5004), ThreadingTCPServer, ()),
        (('192.168.100.10', 6000), ('192.168.100.10', 6001), ThreadingTCPServer, ()),
    ]

If you want to see another example, have a look at the
:download:`active surface <../simulators/active_surface/__init__.py>` module.
The active surface system is composed of 96 listening TCP servers, and in fact
its ``servers`` list in defined in the following way::

    servers = []
    for line in range(96):  # 96 servers
        l_address = ('0.0.0.0', 11000 + line)
        servers.append((l_address, (), ThreadingTCPServer, ()))  # No sending servers or extra args


The ``MultiTypeSystem`` class
--------------------------------

A system can have multiple types. For instance, we have multiple IF distributor
system types, one more simple system, called ``IFD``, and a more complex one,
called ``IFD_14_channels``. Both of them inherits from the ``ListeningSystem``
class, and uses the same server address configuration. Instead of writing two
slightly different modules, along with two different server configurations, we
created a generic IF distributor system, by means of the ``MultiTypeSystem``
class. This class, defined in :download:`common.py <../simulators/common.py>`
acts as a ``class factory``, meaning that given a ``system_type`` parameter,
that must be defined in the module ``__init__`` file, the class gets instanced
with the type defined by the ``system_type`` parameter. For instance, the
default type of the IF distributor is the ``IFD`` one. So, creating a
``System`` object by calling ``if_distributor.System()`` will actually create a
``if_distributor.IFD.System()`` object. If you want to create a
``if_distributor.IFD_14_channels.System()`` object, you have to override the
``system_type`` parameter after importing the ``if_distributor`` module and
before calling ``if_distributor.System()``. If an unknown system type is
provided, the ``MultiTypeSystem`` class ``__new__`` method will raise a
``ValueError``. To check if a system type is known, the ``__new__`` method of
the ``MultiTypeSystem`` class, will check for every ``System`` class present in
all files of the selected system package. The ``MultiTypeSystem`` class is
defined as follows::

    class MultiTypeSystem(object):

        def __new__(self, *args):
            if cls.system_type not in cls.systems:
                raise ValueError(...)

            return cls.systems[cls.system_type].System(*args)

The inherited ``System`` classes must override the ``__new__`` method as
follows::

    class System(MultiTypeSystem):

        def __new__(cls, *args):
            cls.system = systems
            cls.system_type = system_type
            return MultiTypeSystem.__new__(cls, *args)

where ``systems`` is the list of available systems for that particular module
(that can automatically be retrieved calling the ``utils.get_systems()``
function) and ``system_type`` is the variable storing the desired system type
name, this is the variable to override in order to ask for a different system
type. If you want to see additional informations about inheriting the
``MultiTypeSystem`` class take a look at the
:download:`if_distributor <../simulators/if_distributor/__init__.py>` module.


Custom commands
---------------

Custom commands are useful for several use cases.  For instance,
let's suppose we want the simulator to reproduce some error conditions
by changing the ``System`` state.  We just need to define a method that
starts with ``system_``.  I.e::

    class System(BaseSystem):

        def system_generate_error_x(self):
            # Change the state of the System
            ...

After implementing this method, the clients are able to call it
by sending the custom command ``$system_generate_error_x!``.  We can
also define methods with parameters.  In this case the custom
command will be in the form ``$system_commandname:par1,par2,par3!``.

To avoid name clashing, do not head other methods with ``system_``,
so use this convention only for custom commands.
