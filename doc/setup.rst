.. _setup:

*************
Package setup
*************

.. topic:: Preface

   This project requires Python 2.7.
   The following section will guide you through the package setup process.
   Installing the required Python dependencies and the package itself will
   require no longer than 5 minutes.


Install the package
===================
To install the package and its requirements you only need a few minutes. First
of all, after downloading the package, you need to run the following command to
install its Python dependencies:

.. code-block:: shell

   $ pip install -r requirements.txt

This command will automatically install all the required dependencies.
Currently, the only required Python packages are `Numpy <http://www.numpy.org/>`__,
and `Scipy <https://www.scipy.org/>`__.

After the requirements have been installed, it's time to install the package
itself. In order to do so, it is sufficient to execute the following command
inside the repository directory:

.. code-block:: shell

   $ python setup.py install

This command will install all the simulator libraries and scripts into your
Python environment, and you will be able to use it and test it as soon as the
previous command execution is completed.


.. note:: Now that you successfully installed the package, if you want to know
   how to write a simulator, how to run the tests or how to contribute to this
   project, read the :ref:`developer` section. If you just want to know how to
   use the simulators in order to run your code without having to rely on the
   real hardware, then you can jump to the :ref:`user` chapter.
