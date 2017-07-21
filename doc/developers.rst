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
Python standard library.  But we do not want to run only the unit tests:
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

   $ python -m unittest discover tests


Check the testing coverage
--------------------------
If you want to see the percentage of code covered by test,
run the unit tests using `Coverage.py
<https://coverage.readthedocs.io/>`__:

.. code-block:: shell

   $ coverage run -m unittest discover tests

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


Custom commands
===============
Documentation of custom commands (take care that
the custom message's bytes must be different than the
protocol header).


Generate the documentation
==========================
