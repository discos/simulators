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


Development workflow
====================

.. todo:: Write a workflow schema.
   open an issue, create a branch, write a test, write the code and
   related doc, execute the linter, execute the tests, push your branch,
   open a pull request.


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
:download:`active_surface.py <../simulators/active_surface.py>`.

The ``System`` class
--------------------
The ``System`` class must inherit from ``server.BaseSystem``, and
has to define a ``parse()`` method::

    from simulators.common import BaseSystem


    class System(BaseSystem):

        def parse(self, byte):
            ...

The ``System.parse()`` interface is described in `issue #1
<https://github.com/discos/simulators/issues/1>`__.  This method takes one byte
(string of one character, in Python 2) as argument and returns:

* ``False`` when the byte is not the message header and it is still waiting for the header
* ``True`` when it has already got the header and it is composing the message
* the reponse, a non empty string, when there is a response to send back to the
  client.

If the system has nothing to send to the client, as in the case of broadcast
requests, ``System.parse()`` has to return ``True``.
It eventually raises a ``ValueError`` in case there is an unexpected error (not
considered by the protocol).


The ``servers`` list
--------------------
The elements of the ``servers`` list are tuples.  Each tuple is composed
of two items:

* the server ``address``
* a tuple (let's call it ``args``) of possible arguments required
  by ``System.__init__()``.

For instance, let's suppose the system to simulate has 2
servers, the first one with address ``('192.168.100.10', 5000)`` and the
second one with address ``('192.168.100.10', 5001)``.  In that case we have
to define the ``servers`` list as follow::


    servers = [
        ('192.168.100.10', 5000), ()),
        ('192.168.100.10', 5001), ()),
    ]

If our ``System`` class takes some extra arguments, let's say two integers,
we have to pass them throgh the ``args`` tuple.  For instance::

    servers = [
        ('192.168.100.10', 5000), (10, 20)),
        ('192.168.100.10', 5001), (4, 5)),
    ]

If you want to see another example, have a look at the
:download:`active_surface.py <../simulators/active_surface.py>` module.
The active surface system is composed of 96 servers, and in fact its
``servers`` list in defined in the following way::

    servers = []
    for i in range(96):  # 96 servers
        address = ('127.0.0.1', 11000 + s)
        servers.append((address, ()))  # No extra arguments


Custom commands
---------------
Custom commands are useful for several use cases.  For instance,
let's suppose we want the simulator to reproduce some error conditions
by changing the ``System`` state.  We just need to define a method that
starts with double underscore.  I.e::

    class System(BaseSystem):

        def __generate_error_x(self):
            # Change the state of the System
            ...

After implementing this method, the clients are able to call it
by sending the custom command ``$__generate_error_x!``.  We can
also define methods with parameters.  In this case the custom
command will be in the form ``$__command:par1,par2,par3!``.
