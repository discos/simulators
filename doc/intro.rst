.. _intro:

************
Introduction
************

About this project
==================

.. role:: bi
   :class: bolditalic

.. only:: html

   :bi:`DISCOS Simulators`: **a framework for writing hardware simulators for
   the** :bi:`DISCOS` **control software**

.. raw:: latex

   \textbf{\textit{DISCOS Simulators}: a framework for writing hardware
   simulators for the \textit{DISCOS} control software}\\
   Giuseppe Carboni <\texttt{giuseppe.carboni@inaf.it}>
   \vspace{0.5cm}

This document describes the :bi:`DISCOS Simulators` framework. This
framework was designed with the purpose of providing a means to integrate
several hardware simulators of the three Italian radio telescopes
(especially the `Sardinia Radio Telescope`) under the same environment.

Writing a simulator helps the developers in writing good code for the actual
control software of the radio telescope, the :ref:`DISCOS<discos_cs>` control
software. Being able to test the control software code without having to rely
on the hardware represents a huge advantage in the development process, it
provides a way to test each new addition or modification to the code, making
sure that the control software keeps behaving as expected. Furthermore, the
framework allows to test how the control software code reacts under expected
error conditions, in fact, it provides an easy way to simulate unlikely
scenarios that are very difficult or, in some cases, impossible to replicate by
only using the hardware. This allows the developers to write more reliable and
robust code, that is likely capable to allow the user to recover from an error
condition without having to resort to a complete reboot of the system.

Having a fast way to write a simulator of a new incoming device, also allows to
easily verify that the communication protocol on which the software developing
team and the provider of the new device agreed upon, is working as expected. In
case some of the tests yield different results between the simulator and the
real hardware, it is easier to understand which one of the two parties
committed an implementation error, whether it is a bug in the code of the
control software or in the firmware of the device (or just in an update of one
of the two).

In order to do so, it is necessary to have a simulator for each critical
component of the radio telescope. Since the vast majority of the communications
between the control software and the devices (or the simulator, in this case)
are carried on via network, under similar circumstances, having a framework
already capable of handling these kind of communications on its own, is
priceless. It allows the developers to focus on the simulator code and
communication protocol, without having to re-write anything related to the
communication infrastructure, providing the same simple architecture for all
the simulators.

Another important aim of this project is that it opens the possibility of
performing automated tests of the control software code. A suite of simulators,
capable of reproducing various different scenarios, can be exploited to write
and execute a great variety of tests  whenever a modification to the control
software code gets pushed to the main online repository. This workflow is
called `continuous integration`. :cite:`duvall2007continuous`

.. only:: latex

   :ref:`Chapter two<framework>` of this document describes the framework in
   detail, its structure, its layers and the classes that compose it.
   :ref:`Chapter three<user>` explains how to install the package and run the
   simulators. :ref:`Chapter four<developer>` goes into detail in describing
   how to write a new simulator, test it, and integrate it into the framework.
   In :ref:`chapter five<utils>`, the reader will find the documentation of the
   `utils` library, which contains several useful functions to easily perform
   some recurrent tasks such as format conversions.


.. _discos_cs:

The `DISCOS` Control Software
=============================
Taken from the `DISCOS` official document:

`"`:bi:`DISCOS` (:bi:`D`\ `evelopment of the` :bi:`I`\ `talian` :bi:`S`\
`ingle-dish` :bi:`CO`\ `ntrol` :bi:`S`\ `ystem) is the control software
produced for the Italian radio telescopes. It is a distributed system based
on` :bi:`ACS` (:bi:`A`\ `LMA` :bi:`C`\ `ommon` :bi:`S`\ `oftware),
commanding all the devices of the telescope and allowing the user to
perform single-dish observations in the most common modes. As of today, the
code specifically implemented for the telescopes (i.e. excluding the huge
ACS framework) amounts to about 650000 lines. Even VLBI (or guest-backend)
observations partly rely on DISCOS, as it must be used to perform the focus
selection and the frontend setup."`:cite:`DISCOS`


Da inserire immagine di discos-console
