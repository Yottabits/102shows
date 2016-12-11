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

    def __init__(self, num_leds: int, max_clock_speed_hz: int = 4000000, initial_brightness: int = 100):
        super().__init__(num_leds, max_clock_speed_hz, initial_brightness)  #
        self.color_buffer = [(0, 0, 0)] * self.num_leds
        self.brightness_buffer = [initial_brightness] * self.num_leds

    def set_pixel(self, led_num, red, green, blue) -> None:
        self.color_buffer[led_num] = (red, green, blue)

    def get_pixel(self, led_num):
        return self.color_buffer[led_num]

    def set_brightness(self, led_num: int, brightness: int) -> None:
        self.brightness_buffer[led_num] = brightness

    def rotate(self, positions=1):
        self.color_buffer = self.color_buffer[positions:] + self.color_buffer[:positions]

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
