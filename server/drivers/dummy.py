"""
Dummy Driver
(c) 2016 Simon Leiner
"""

import logging as log
from multiprocessing import Array as SyncedArray

from drivers import LEDStrip


class DummyDriver(LEDStrip):
    """
    A Dummy Driver that just shows the LED states on the log.
    This can be useful for developing without having a real LED strip at hand.
    """

    def __init__(self, num_leds: int, max_clock_speed_hz: int = 4000000, initial_brightness: int = 100):
        super().__init__(num_leds, max_clock_speed_hz, initial_brightness)  #
        self.red_buffer = [0] * self.num_leds
        self.green_buffer = [0] * self.num_leds
        self.blue_buffer = [0] * self.num_leds
        self.brightness_buffer = [initial_brightness] * self.num_leds

        self.synced_red_buffer = SyncedArray('i', self.red_buffer)
        self.synced_green_buffer = SyncedArray('i', self.green_buffer)
        self.synced_blue_buffer = SyncedArray('i', self.blue_buffer)
        self.synced_brightness_buffer = SyncedArray('i', self.brightness_buffer)

    def _set_pixel(self, led_num, red, green, blue) -> None:
        self.red_buffer[led_num] = red
        self.green_buffer[led_num] = green
        self.blue_buffer[led_num] = blue

    def get_pixel(self, led_num):
        red = self.red_buffer[led_num]
        green = self.green_buffer[led_num]
        blue = self.blue_buffer[led_num]
        return red, green, blue

    def _set_brightness(self, led_num: int, brightness: int) -> None:
        self.brightness_buffer[led_num] = brightness

    def rotate(self, positions=1):
        self.red_buffer = self.red_buffer[positions:] + self.red_buffer[:positions]
        self.green_buffer = self.green_buffer[positions:] + self.green_buffer[:positions]
        self.blue_buffer = self.blue_buffer[positions:] + self.blue_buffer[:positions]

    def show(self) -> None:
        log.debug("FAKE LED STRIP SHOWS: ")
        for led_num in range(self.num_leds):
            red, green, blue = self.get_pixel(led_num)
            brightness = self.brightness_buffer[led_num]
            log.debug("{led:03d} => ({r:03d},{g:03d},{b:03d}) @ {brightness:.2f}".format(led=led_num,
                                                                                         r=red,
                                                                                         g=green,
                                                                                         b=blue,
                                                                                         brightness=brightness))

    def sync_up(self) -> None:
        """ write to the synced buffer """
        for led_num in range(self.num_leds):
            self.synced_red_buffer[led_num] = self.red_buffer[led_num]
            self.synced_green_buffer[led_num] = self.green_buffer[led_num]
            self.synced_blue_buffer[led_num] = self.blue_buffer[led_num]
            self.synced_brightness_buffer[led_num] = self.brightness_buffer[led_num]

    def sync_down(self) -> None:
        """ read from the synced buffer """
        for led_num in range(self.num_leds):
            self.red_buffer[led_num] = self.synced_red_buffer[led_num]
            self.green_buffer[led_num] = self.synced_green_buffer[led_num]
            self.blue_buffer[led_num] = self.synced_blue_buffer[led_num]
            self.brightness_buffer[led_num] = self.synced_brightness_buffer[led_num]
