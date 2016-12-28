"""
102shows.Drivers
(c) 2016 Simon Leiner
licensed under the GNU Public License, version 2

This module contains the drivers for the LED strips
"""

import logging
from abc import ABCMeta, abstractmethod
from multiprocessing import Array as SyncedArray

__all__ = ['apa102', 'dummy', 'LEDStrip']

logger = logging.getLogger('102shows.drivers')


class LEDStrip(metaclass=ABCMeta):
    """
    This class provides the general interface for LED drivers that the lightshows use.
    All LED drivers for 102shows should inherit this class.
    The following restrictions apply:
        - pixel order is r,g,b
        - pixel resolution (number of dim-steps per color component) is 8-bit, so 0 - 255
    """

    max_refresh_time_sec = 1  #: this is used for optimizations of sleep()

    def __init__(self, num_leds: int, max_clock_speed_hz: int = 4000000):
        """
        stores the given parameters and initializes the color and brightness buffers
        drivers should extend this method

        :param num_leds: number of LEDs in the strip
        :param max_clock_speed_hz: maximum clock speed (Hz) of the bus
        """
        # store the given parameters
        self.num_leds = num_leds
        self.max_clock_speed_hz = max_clock_speed_hz

        # private variables
        self.__frozen = False

        # buffers
        self.color_buffer = [(0.0, 0.0, 0.0)] * self.num_leds
        self.brightness_buffer = [0] * self.num_leds

        self.synced_red_buffer = SyncedArray('f', [0.0] * self.num_leds)
        self.synced_green_buffer = SyncedArray('f', [0.0] * self.num_leds)
        self.synced_blue_buffer = SyncedArray('f', [0.0] * self.num_leds)
        self.synced_brightness_buffer = SyncedArray('i', self.brightness_buffer)

    def __del__(self):
        """ invokes self.close() and deletes all the buffers"""
        self.close()

        del self.color_buffer, self.synced_red_buffer, self.synced_green_buffer, self.synced_blue_buffer
        del self.brightness_buffer, self.synced_brightness_buffer

        logger.info("Driver successfully closed")

    @abstractmethod
    def close(self):
        """ close the bus connection and clean up remains"""
        pass

    def freeze(self):
        """
        freezes the strip. All state-changing methods (on_color_change() and on_brightness_change())
        will not do anything anymore and leave the buffer unchanged
        """
        self.__frozen = True

    def unfreeze(self):
        """ revokes all effects of freeze() """
        self.__frozen = False

    def get_pixel(self, led_num):
        """
        gets the pixel at index led_num

        :param led_num: the index of the pixel you want to get
        :return: (red, green, blue) tuple
        """

        return self.color_buffer[led_num]

    def set_pixel(self, led_num: int, red: float, green: float, blue: float) -> None:
        """
        subclasses should not inherit this method!
        writes the color buffer and calls on_color_change() if not frozen
        """

        if led_num < 0:
            return  # Pixel is invisible, so ignore
        if led_num >= self.num_leds:
            return  # again, invsible

        if not self.__frozen:
            self.color_buffer[led_num] = (red, green, blue)
            self.on_color_change(led_num, red, green, blue)

    @abstractmethod
    def on_color_change(self, led_num, red: float, green: float, blue: float) -> None:
        """
        changes the message buffer after a pixel was changed in the global color buffer
        To send the buffer to the strip and show the changes, invoke strip.show()

        :param led_num: index of the RGB pixel to be changed
        :param red: new red component
        :param green: new green component
        :param blue: new blue component
        """

    def set_pixel_bytes(self, led_num: int, rgb_color):
        """
        Changes the pixel led_num to the given color IN THE BUFFER!
        To send the buffer to the strip and show the changes, invoke strip.show()
        If you do not know, how rgb_color works, just use set_pixel()

        :param led_num: index of the RGB pixel to be changed
        :param rgb_color: a 3-byte RGB color value represented as a base-10 integer
        :return:
        """
        red, green, blue = self.color_bytes_to_tuple(rgb_color)
        self.set_pixel(led_num, red, green, blue)

    @staticmethod
    def color_tuple_to_bytes(red: float, green: float, blue: float) -> int:
        """
        converts an RGB color tuple into a 3-byte color value

        :param red: red component of the tuple
        :param green: green component of the tuple
        :param blue: blue component of the tuple
        :return: the tuple components are joined into a 3-byte value with each byte representing a color component
        """

        # round to integers
        red = round(red)
        green = round(green)
        blue = round(blue)

        return (red << 16) + (green << 8) + blue

    @staticmethod
    def color_bytes_to_tuple(rgb_color: int):
        """
        converts a 3-byte color value into an RGB color tuple

        :param rgb_color: a 3-byte RGB color value represented as a base-10 integer
        :return: color tuple (r,g,b)
        """
        r = (rgb_color & 0xFF0000) >> 16
        g = (rgb_color & 0x00FF00) >> 8
        b = rgb_color & 0x0000FF
        return r, g, b

    @abstractmethod
    def show(self) -> None:
        """
        This method should show the buffered pixels on the strip,
        e.g. write the pixel buffer to the port on which the strip is connected.

        :return: none
        """
        pass

    def rotate(self, positions=1):
        """
        Treating the internal leds array as a circular buffer, rotate it by the specified number of positions.
        The number could be negative, which means rotating in the opposite direction.

        :param positions: rotate by how many steps
        """
        self.color_buffer = self.color_buffer[positions:] + self.color_buffer[:positions]
        for led_num in range(self.num_leds):
            r, g, b = self.get_pixel(led_num)
            self.on_color_change(led_num, r, g, b)

    def set_brightness(self, led_num: int, brightness: int) -> None:
        """
        sets the brightness for a single LED in the strip

        :param led_num: the target LED index
        :param brightness: the desired brightness (0 - 100)
        """
        if not self.__frozen:
            self.brightness_buffer[led_num] = brightness
            self.on_brightness_change(led_num)

    @abstractmethod
    def on_brightness_change(self, led_num: int) -> None:
        """
        reacts to a brightness change at led_num by modifying the message buffer

        :param led_num: number of the LED whose brightness was modified
        """
        pass

    def set_global_brightness(self, brightness: int) -> None:
        """
        calls set_brightness() for all LEDs in the strip

        :param brightness: the brightness (0 - 100) to be set all over the strip
        """
        for led_num in range(self.num_leds):
            self.set_brightness(led_num, brightness)

    def clear_buffer(self) -> None:
        """ sets all pixels in the color buffer to (0,0,0) """
        for led_num in range(self.num_leds):
            self.set_pixel(led_num, 0, 0, 0)

    def clear_strip(self) -> None:
        """ clears the color buffer, then invokes a blackout on the strip by calling show() """
        self.clear_buffer()
        self.show()

    def sync_up(self) -> None:
        """ copies the local message buffer to a shared object so other processes can see the current strip state """
        logger.info("sync-up")
        for led_num, (red, green, blue) in enumerate(self.color_buffer):
            # colors
            self.synced_red_buffer[led_num] = red
            self.synced_green_buffer[led_num] = green
            self.synced_blue_buffer[led_num] = blue

            # brightness
            self.synced_brightness_buffer[led_num] = self.brightness_buffer[led_num]

    def sync_down(self) -> None:
        """ applies the shared buffer to the local message buffer """
        logger.info("sync-down")
        for led_num, _ in enumerate(self.color_buffer):
            # colors
            red = self.synced_red_buffer[led_num]
            green = self.synced_green_buffer[led_num]
            blue = self.synced_blue_buffer[led_num]
            self.color_buffer[led_num] = (red, green, blue)
            self.on_color_change(led_num, red, green, blue)

            # brightness
            self.brightness_buffer[led_num] = self.synced_brightness_buffer[led_num]
            self.on_brightness_change(led_num)
