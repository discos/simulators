.. _developer:

************************
Developers documentation
************************

.. topic:: Preface

   If you want to know how to write a simulator, how to run the
   tests or how to contribute to this project, then you have to read
   this section.  If you just want to know how to use the simulators
   in order to run your code without the real hardware, then you
   should read the :ref:`user` chapter.  This project requires Python 2.7.


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

The ``SendingSystem`` class and the ``System.get_message()`` method
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If the ``System`` class inherits from ``server.SendingSystem``, it has to define
a ``get_message()`` method and a ``sampling_rate`` attribute::

    from simulators.common import SendingSystem


    class System(SendingSystem):

        self.sampling_rate = ...

        def get_message(self):
            ...

The ``System.get_message()`` method should return some arbitrary data that the system
would like to send to its client(s). The ``System.sampling_rate`` attribute should be a
strictly positive integer or floating point number, it represents the time interval
(in seconds) between each message sent by the system.

Inheriting from both ``ListeningSystem`` and ``SystemSystem``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A ``System`` class can inherit from both ``ListeningSystem`` and ``SendingSystem`` at
the same time. If it does, it has to implement both the ``System.parse()`` and the
``System.get_message()`` methods, along with the ``System.sampling_rate`` value.


The ``servers`` list
--------------------

The elements of the ``servers`` list are tuples.  Each tuple is composed
of three items:

* the server listening address, ``l_address``
* the server sending address, ``s_address``
* another tuple (let's call it ``args``) of possible arguments required
  by ``System.__init__()``.

Each element of the ``servers`` list represents an instance of the ``system``,
``l_address`` is the address in which the server will wait for its clients
to send the commands to pass to the ``System.parse()`` method. ``s_address`` is
the address from which the server will send its data retrieved via the
``System.get_message()`` method, at a constant period of ``System.sampling_rate``
seconds.

For instance, let's suppose the system to simulate has 2 listening servers
and no sending servers, the first one with address ``('192.168.100.10', 5000)``
and the second one with address ``('192.168.100.10', 5001)``.  In that case
we have to define the ``servers`` list as follows::

    servers = [
        ('192.168.100.10', 5000), (), ()),
        ('192.168.100.10', 5001), (), ()),
    ]

If our ``System`` class takes some extra arguments, let's say two integers,
we have to pass them throgh the ``args`` tuple.  For instance::

    servers = [
        ('192.168.100.10', 5000), (), (10, 20)),
        ('192.168.100.10', 5001), (), (4, 5)),
    ]

If the system we want to simulate has instead 3 sending servers and no listening
servers, we have to define the ``servers`` list as follows::

    servers = [
        ((), ('192.168.100.10', 5002), ()),
        ((), ('192.168.100.10', 5003), ()),
        ((), ('192.168.100.11', 5000), ()),
    ]

Finally, a system instance can act as both listening and sending server. In this case,
each server list entry must be defined as follows::

    servers = [
        (('192.168.100.10', 5003), ('192.168.100.10', 5004), ()),
        (('192.168.100.10', 6000), ('192.168.100.10', 6001), ()),
    ]

If you want to see another example, have a look at the
:download:`active surface <../simulators/active_surface/__init__.py>` module.
The active surface system is composed of 96 listening servers, and in fact
its ``servers`` list in defined in the following way::

    servers = []
    for line in range(96):  # 96 servers
        l_address = ('127.0.0.1', 11000 + line)
        servers.append((l_address, (), ()))  # No sending servers or extra args


The ``ConfigurableSystem`` class
--------------------------------

A system can have multiple configurations. For instance, we have multiple
IF distributor systems, a simpler one, called ``IFD``, and a more complex one,
called ``IFD_14_channels``. Both of them inherits from the ``ListeningSystem``
class, and uses the same server configuration. Instead of writing two
different systems, along with two different server configurations, we
created a generic IF distributor system, by means of the ``ConfigurableSystem``
class. This class, defined in
:download:`common.py <../simulators/common.py>` acts as a ``class factory``,
meaning that given a ``system_type`` parameter, that must be defined in the
module ``__init__`` file, the class gets instanced with the type defined by the
``system_type`` parameter. For instance, the default configuration for the
IF distributor is the ``IFD`` one. So, creating an object calling
``if_distributor.System()`` will actually instance a ``if_distributor.IFD.System()``
object. If you want to create a ``if_distributor.IFD_14_channels.System()``
object, you have to modify the ``system_type`` parameter after importing the
``if_distributor`` module and before calling ``if_distributor.System()``.
If an unknown configuration is given, the ``ConfigurableSystem`` class
``__new__`` method will raise a ``ValueError``. To check if a configuration
is known, the ``__new__`` method of the ``ConfigurableSystem`` class, will
check for every ``System`` class present in all files of the selected system
package.


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


.. _api:

API
===
This part of the documentation covers all interfaces.  For
parts where Simulators depends on external libraries, we document the most
important right here and provide links to the canonical documentation.

Server module
-------------

.. module:: simulators.server


Handler classes
~~~~~~~~~~~~~~~

.. autoclass:: ListenHandler
   :members:
   :inherited-members:


.. autoclass:: SendHandler
   :members:
   :inherited-members:


Server class
~~~~~~~~~~~~

.. autoclass:: Server
   :members:


Simulator class
~~~~~~~~~~~~~~~

.. autoclass:: Simulator
    :members:
    :inherited-members:


Active Surface module
---------------------

.. module:: simulators.active_surface


System class
~~~~~~~~~~~~

.. autoclass:: System
   :members:
   :inherited-members:


USD class
~~~~~~~~~~~~

.. autoclass:: USD
   :members:
   :inherited-members:


ACU module
---------------------------

.. module:: simulators.acu


System class
~~~~~~~~~~~~

.. autoclass:: System
    :members:
    :inherited-members:


Axis_status class
~~~~~~~~~~~~~~~~~

.. autoclass:: MasterAxisStatus
    :members:
    :inherited-members:
    :private-members:


IF Distributor module
---------------------

.. module:: simulators.if_distributor


System class
~~~~~~~~~~~~

.. autoclass:: System
    :members:
    :inherited-members:


Useful Functions and Classes
----------------------------

.. module:: simulators.utils

.. autofunction:: checksum

.. autofunction:: binary_complement

.. autofunction:: twos_to_int

.. autofunction:: int_to_twos

.. autofunction:: binary_to_bytes

.. autofunction:: bytes_to_int

.. autofunction:: int_to_bytes

.. autofunction:: bytes_to_uint

.. autofunction:: uint_to_bytes

.. autofunction:: real_to_binary

.. autofunction:: real_to_bytes

.. autofunction:: bytes_to_real

.. autofunction:: sign

.. autofunction:: mjd

.. autofunction:: mjd_to_date

.. autofunction:: day_microseconds

.. autofunction:: day_milliseconds

.. autofunction:: day_percentage
