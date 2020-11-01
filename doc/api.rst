.. _api:

***
API
***

.. topic:: Preface

   This part of the documentation covers all interfaces of the framework and
   its libraries.


Common module
=============

.. module:: simulators.common


BaseSystem class
----------------

.. autoclass:: BaseSystem
   :members:
   :inherited-members:


ListeningSystem class
---------------------

.. autoclass:: ListeningSystem
   :members:
   :inherited-members:


SendingSystem class
-------------------

.. autoclass:: SendingSystem
   :members:
   :inherited-members:


MultiTypeSystem class
---------------------

.. autoclass:: MultiTypeSystem
   :members:
   :inherited-members:

   .. automethod:: __new__


Server module
=============

.. module:: simulators.server


Handler classes
---------------

.. autoclass:: BaseHandler
   :members:
   :inherited-members:


.. autoclass:: ListenHandler
   :members:
   :inherited-members:


.. autoclass:: SendHandler
   :members:
   :inherited-members:


Server class
------------

.. autoclass:: Server
   :members:


Simulator class
---------------

.. autoclass:: Simulator
   :members:
   :inherited-members:


The Utils library
=================

.. module:: simulators.utils

.. autofunction:: checksum

.. autofunction:: binary_complement

.. autofunction:: twos_to_int

.. autofunction:: int_to_twos

.. autofunction:: binary_to_bytes

.. autofunction:: bytes_to_int

.. autofunction:: bytes_to_binary

.. autofunction:: bytes_to_uint

.. autofunction:: real_to_binary

.. autofunction:: real_to_bytes

.. autofunction:: bytes_to_real

.. autofunction:: int_to_bytes

.. autofunction:: uint_to_bytes

.. autofunction:: sign

.. autofunction:: mjd

.. autofunction:: mjd_to_date

.. autofunction:: day_microseconds

.. autofunction:: day_milliseconds

.. autofunction:: day_percentage

.. _get_multitype_systems:
.. autofunction:: get_multitype_systems

.. autofunction:: list_simulators
