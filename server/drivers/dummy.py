"""
Fake Driver
(c) 2016 Simon Leiner

A Dummy Driver that does not need any interface
"""

import logging as log

from drivers.apa102 import LEDStrip


class DummyDriver(LEDStrip):
    def show(self) -> None:
        log.debug("FAKE LED STRIP SHOWS: ")
        for led_num in range(self.num_leds):
            red, green, blue = self.color_buffer[led_num]
            brightness = self.brightness_buffer[led_num]
            log.debug("{led:03d} => ({r:03d},{g:03d},{b:03d}) @ {brightness:.2f}".format(led=led_num,
                                                                                         r=red,
                                                                                         g=green,
                                                                                         b=blue,
                                                                                         brightness=brightness))

    def initialize_strip_connection(self):
        log.debug("init")
