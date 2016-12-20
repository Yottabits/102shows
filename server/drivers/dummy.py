"""
Dummy Driver
(c) 2016 Simon Leiner
licensed under the GNU Public License, version 2
"""

import logging

from drivers import LEDStrip

logger = logging.getLogger('102shows.server.drivers.dummy')


class DummyDriver(LEDStrip):
    """
    A Dummy Driver that just shows the LED states on the logger.
    This can be useful for developing without having a real LED strip at hand.
    """

    def on_color_change(self, led_num, red: float, green: float, blue: float) -> None:
        pass

    def on_brightness_change(self, led_num: int) -> None:
        pass

    def show(self) -> None:
        logger.debug("FAKE LED STRIP SHOWS: ")
        for led_num in range(self.num_leds):
            red, green, blue = self.get_pixel(led_num)
            brightness = self.brightness_buffer[led_num]
            logger.debug("{led:03d} => ({r:05.1f}, {g:05.1f}, {b:05.1f}) @ {brightness:.2f}"
                         .format(led=led_num,
                                 r=red,
                                 g=green,
                                 b=blue,
                                 brightness=brightness))

    def close(self):
        pass
