===================
Developer Reference
===================

This will give you an overview of all the classes in 102shows.


#####################
:py:mod:`mqttcontrol`
#####################

The MQTT controller is the essential idea of 102shows:
Starting and controlling lightshows via MQTT without making
lightshow development very hard.

The MQTT controller takes care of reading the configuration
file and initializing the LED strip with the right driver,
providing the MQTT interface for starting and stopping shows
(of course) and it ensures that only one lightshow is running
at the same time. You can think of it as the "main function"
of 102shows that is starting and controlling all things that
happen.

.. autoclass:: mqttcontrol.MQTTControl
   :members:


#################
:py:mod:`drivers`
#################

Structure
=========

102shows is designed to work with several types of LED strips.
Currently, only APA102 (aka Adafruit DotStar) chips are supported
but other chipsets will be included in the future.

There is also a Dummy driver included.
It does not control any LED strip. It merely manages similar internal
buffers as a "normal" driver and if :py:func:`drivers.dummy.DummyDriver.show`
is called, it will print the state of all LEDs in the hypothetical strip
to the debug output. This is particular useful for tests on a machine
with no actual LED strip attached.

To be able to effortlessly switch between drivers, there is a common
interface: All drivers should base on the class :py:mod:`drivers.LEDStrip`
and be located under :file:`/path/to/102shows/server/drivers`.

.. note::
   For 102shows to find and use the driver, it must have an entry in both
   :py:attr:`drivers.__all__` and :py:attr:`drivers.__active__.drivers`.



Interface
=========

.. module:: drivers
   :synopsis: LED Strip drivers

.. autoclass:: drivers.LEDStrip
   :members:



#################
:py:mod:`helpers`
#################

Overview
========

.. automodule:: helpers

.. autofunction:: helpers.get_logo
.. autofunction:: helpers.get_version

color
=====

.. automodule:: helpers.color
   :members:

configparser
============

.. automodule:: helpers.configparser
   :members:

exceptions
==========

see Exceptions (#fixme: link)

mqtt
====

.. automodule:: helpers.mqtt
   :members:

preprocessors
=============

.. automodule:: helpers.preprocessors
   :members:

verify
======

.. automodule:: helpers.verify
   :members:

Tests
-----

.. automodule:: helpers.test_verify
   :members:


####################
:py:mod:`lightshows`
####################

Overview
========

.. automodule:: lightshows
   :synopsis: LED animations



Templates
=========

.. todo:: include link to controller

.. automodule:: lightshows.templates
   :synopsis: useful templates for writing specific lightshows

The base template
-----------------

As the name says, this is the most basic template.
All lightshows (and all other templates) rely on this template.
It offers quite a lot:

   - The interface to the controller:
      - :py:func:`lightshows.base.Lightshow.name` returns the name of the lightshow
      - :py:func:`lightshows.base.Lightshow.start` initializes the show process,
         starts the built-in MQTT client and then triggers the start of the animation
      - :py:func:`lightshows.base.Lightshow.stop` can be called to gracefully end the show
      - :py:func:`lightshows.base.Lightshow.name`




.. autoclass:: lightshows.templates.base.Lightshow
   :members:

##########
Exceptions
##########

.. automodule:: helpers.exceptions
   :members:
