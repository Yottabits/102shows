"""
Dummy Driver
(c) 2016 Simon Leiner
"""

import logging as log

from drivers import LEDStrip


class DummyDriver(LEDStrip):
    """
    A Dummy Driver that just shows the LED states on the log.
    This can be useful for developing without having a real LED strip at hand.
    """

    def on_color_change(self, led_num, red: float, green: float, blue: float) -> None:
        pass

    def on_brightness_change(self, led_num: int) -> None:
        pass

    def show(self) -> None:
        log.debug("FAKE LED STRIP SHOWS: ")
        for led_num in range(self.num_leds):
            red, green, blue = self.get_pixel(led_num)
            brightness = self.brightness_buffer[led_num]
            log.debug("{led:03d} => ({r:03.1f},{g:03.1f},{b:03.1f}) @ {brightness:.2f}".format(led=led_num,
                                                                                               r=red,
                                                                                               g=green,
                                                                                               b=blue,
                                                                                               brightness=brightness))
