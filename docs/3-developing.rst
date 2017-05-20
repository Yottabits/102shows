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

The general scheme is ``{prefix}/{sys_name}/show/{show_name}/{command}``

Switching a show
================

Starting a show
---------------

   - **topic**: ``{prefix}/{sys_name}/show/start``
   - **payload**: JSON Object, for example:

      .. code-block:: json

         {
            "name": "name_of_my_show",
            "parameters": {
               "some_time_sec": 3.5,
               "arbitrary_color": [255, 64, 8]
            }
         }

      The ``parameters`` block is optional.

   - **retained**: no

Stopping a show
---------------

   - **topic**: ``{prefix}/{sys_name}/show/stop``
   - **payload**: none needed
   - **retained**: no

Response of the system
----------------------

   - **topic**: ``{prefix}/{sys_name}/show/current``
   - **payload**: show name as string
   - **retained**: yes

The system is sending this message every time the current show is changed.

Global brightness
=================

Setting the global brightness
-----------------------------

   - **topic**: ``{prefix}/{sys_name}/global-brightness/set``
   - **payload**: string containing a floating-point number between 0.0 and 1.0
   - **retained**: no

Response of the system
----------------------

   - **topic**: ``{prefix}/{sys_name}/global-brightness/current``
   - **payload**: string containing a floating-point number between 0.0 and 1.0
   - **retained**: yes

The system is sending this message every time the brightness is changed.

Show-specific parameters
========================

Setting a parameter
-------------------

   - **topic**: ``{prefix}/{sys_name}/show/{show-name}/parameters/set``
   - **payload**: JSON
   - **retained**: no

Response of the system
----------------------

   - **topic**: ``{prefix}/{sys_name}/show/{show-name}/parameters/current``
   - **payload**: JSON with all the parameters, for example:

      .. code-block:: json

         {
            "some_time_sec": 3.5,
            "arbitrary_color": [255, 64, 8]
         }

   - **retained**: yes

The system is sending this message every time the parameter is changed.

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
The name of the parameter must not be ``start`` or ``stop``


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

creating a ``lightshows`` object
--------------------------------
It is really simple: ::

   my_show_object = lightshows.__active__.shows['commonnameofthelightshow'](strip, parameters)

You could access the lightshow class directly, but the 102shows convention is to access the class
by its common name in the ``shows`` array under :py:mod:`lightshows.active`

There are two arguments that you have to pass to the constructor:

* ``strip``: A :py:class:`drivers.LEDStrip` object representing your strip
* ``parameters``: A :py:class:`dict` mapping parameter names (of the lightshow) to the parameter values,
  for example: ::

      parameters = {'example_rgb_color': (255,127,8),
                    'an_arbitrary_fade_time_sec': 1.5}

**See also:** The documentation of :py:class:`lightshows.templates.base.Lightshow`

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
