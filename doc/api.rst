.. _api:

***
API
***

.. topic:: Preface

    This part of the documentation covers all interfaces.  For
    parts where Simulators depends on external libraries, we document the most
    important right here and provide links to the canonical documentation.


Common module
=============

.. module:: simulators.common


BaseSystem class
~~~~~~~~~~~~~~~~

.. autoclass:: BaseSystem
   :members:
   :inherited-members:


ListeningSystem class
~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: ListeningSystem
   :members:
   :inherited-members:


SendingSystem class
~~~~~~~~~~~~~~~~~~~

.. autoclass:: SendingSystem
   :members:
   :inherited-members:


MultiTypeSystem class
~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: MultiTypeSystem
   :members:
   :inherited-members:


Server module
=============

.. module:: simulators.server


Handler classes
~~~~~~~~~~~~~~~

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
~~~~~~~~~~~~

.. autoclass:: Server
   :members:


Simulator class
~~~~~~~~~~~~~~~

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


Active Surface module
=====================

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
==========

.. module:: simulators.acu


System class
~~~~~~~~~~~~

.. autoclass:: System
   :members:
   :inherited-members:


GeneralStatus class
~~~~~~~~~~~~~~~~~~~~

.. autoclass:: GeneralStatus
   :members:
   :inherited-members:


SimpleAxisStatus class
~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: simulators.acu.axis_status.SimpleAxisStatus
   :members:
   :inherited-members:


MasterAxisStatus class
~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: simulators.acu.axis_status.MasterAxisStatus
   :members:
   :inherited-members:


MotorStatus class
~~~~~~~~~~~~~~~~~

.. autoclass:: simulators.acu.motor_status.MotorStatus
   :members:
   :inherited-members:


PointingStatus class
~~~~~~~~~~~~~~~~~~~~

.. autoclass:: PointingStatus
   :members:
   :inherited-members:


IF Distributor module
=====================

.. module:: simulators.if_distributor


System class
~~~~~~~~~~~~

.. autoclass:: System
   :members:
   :inherited-members:
