=======================
Developing for 102shows
=======================

####
MQTT
####

The 102shows server can be controlled completely via MQTT.
On this page, you see the commands it responds to.

Paths
=====

The general scheme is ``led/{sys_name}/show/{show_name}/{command}``

General commands
----------------

The MQTT controller listens for the commands ``start`` and ``stop`` for all shows,
and all shows (should) respond to the ``brightness`` command.
Any other commands (so all except for ``start``, ``stop`` and ``brightness``)
are up to the individual lightshow.

``start``
^^^^^^^^^
.. todo:: fix method links

The MQTT controller stops (see below) any running show.
Then it checks if the given parameters (the JSON payload of the MQTT start message)
are valid by invoking ``show.check_runnable()``.
If the show calls the parameters valid, the controller starts a new process
that runs the method ``show.run(strip, parameters)``.

``stop``
^^^^^^^^
The MQTT controller asks the lightshow process kindly to join by sending
SIGINT to the show process.
The Lightshow base template implements a handler for this signal and usually
saves the current strip state and joins after a few milliseconds.
However, if the process does not join after 1 second, it is terminated by the controller.

``brightness``
^^^^^^^^^^^^^^
This command is handled by lightshows (in earlier versions, the controller
handled brightness changes - but two processes accessing the same strip at
the same time causes a lot of trouble).
They change the brightness of a strip. Payload is a float from 0 to 100.

Lightshow-specific commands
---------------------------

Each lightshow can implement its own commands, like ``foo-color``, ``velocity`` (of an animation) etc.


##########
Lightshows
##########

Formal interface
================

* any show should reside in its own file (*aka module*) under ``server/lightshows/``
   *for example:* ``myshow.py``

* the module must be registered in the list ``__all__`` in :py:mod:`lightshows`
   *for example:* ::

      __all__ = ['foo', 'bar', 'myshow']

* all lightshows should inherit the basic lightshow template under :py:mod:`lightshows.templates.base`
   *for example:* ::

      from lightshows.templates.base import *

      def MyShow(Lightshow):
          def run(self):
              ...

          def check_runnable(self):
              ...

          def set_parameter(self):
              ...

* it must be registered under ``shows`` in :py:mod:`config` file
   *for example:* ::

      configuration.shows('MyShow') = myshow.MyShow

class parameters
----------------
.. todo:: explain class parameters

Example
-------

a lightweight example is :py:mod:`lightshows.solidcolor`

.. module:: lightshows.solidcolor
.. literalinclude:: ../server/lightshows/solidcolor.py
   :linenos:

Other templates
===============

.. todo:: explain other templates

``ColorCycle``
--------------
.. todo:: explain color cycle
