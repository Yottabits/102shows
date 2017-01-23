======================
Supported LED chipsets
======================

#############################
APA102 (aka Adafruit DotStar)
#############################

The `APA102 <https://www.adafruit.com/products/2343>`_  is an RGB LED with an
integrated driver chip that can be addressed via SPI.
That makes it ideal for the Raspberry Pi as talking to an SPI device from Python
is really easy.
Another advantage of this chip is its support for high SPI data rates (for short
strips of less than 200 LEDs you can easily do 8 MHz) which results in very high
framerates and smooth-looking animations.

You can find cheap strips on AliExpress etc. or buy them at Adafruit - they sell
them as `DotStar <https://www.adafruit.com/products/2240>`_.

This driver was originally written by `tinue <https://github.com/tinue/APA102_Pi>`_
and can be found `here <https://github.com/tinue/APA102_Pi>`_.

.. autoclass:: drivers.apa102.APA102
   :members:
   :inherited-members:


###########################
No LED Strip (Dummy Driver)
###########################

.. autoclass:: drivers.dummy.DummyDriver
   :members:
   :inherited-members: