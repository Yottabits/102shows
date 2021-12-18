========
102shows
========

*Raspberry Pi + APA102 + MQTT + 102shows = LED awesomeness!*

|Code Climate|  |Documentation Status|

----

**THERE IS CURRENTLY NO ACTIVE MAINTAINER FOR THIS PROJECT.**
If you want to take over the maintenance for this project, go ahead and open an issue ticket.

----

102shows is an LED strip driver for the Raspberry Pi and also a collection of lightshows.
These lightshows can be controlled over your home network via MQTT.
And for those who do not prefer sending raw MQTT messages from the console, there is a
(`Node-RED <https://nodered.org>`__-based) web interface.
Its responsive layout makes it ideal for smart phones, tablets and computers.

Supported LED chipsets
----------------------

- `APA102 <https://www.aliexpress.com/item//32322326979.html>`__ (a.k.a
  `DotStar <https://www.adafruit.com/products/2240>`__)
- `SK9822 <https://cpldcpu.com/2016/12/13/sk9822-a-clone-of-the-apa102/>`__

Features
--------

-  `non-linear brightness perception
   correction <https://ledshield.wordpress.com/2012/11/13/led-brightness-to-your-eye-gamma-correction-no/>`__
   (commonly mistaken as *gamma correction*)
-  High framerates even with long strips (over 140 refreshes per seconds
   at a strip length of 500 LEDs)
-  sleek looking UI (based on `Node-RED <https://nodered.org>`__)
-  easily controllable via MQTT messages
-  glitch obliteration
-  easily configurable (see a
   `sample <https://gist.github.com/sleiner/dd967b20d555e78f1d3d67b7aa49324a>`__)
-  simple
   `API <https://github.com/Yottabits/102shows/wiki/Lightshow-modules>`__
   for writing your own lightshows
-  pure Python 3

Installation
------------

Take a look at the `Documentation <https://102shows.readthedocs.io/en/latest/1-usage.html#installation>`__

Questions? 🤔
------------

Write an e-mail to me: 102shows@leiner.me

.. |Code Climate| image:: https://codeclimate.com/github/Yottabits/102shows/badges/gpa.svg
   :target: https://codeclimate.com/github/Yottabits/102shows
   :alt: Code Climate

.. |Documentation Status| image:: https://readthedocs.org/projects/102shows/badge
   :target: http://102shows.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status
