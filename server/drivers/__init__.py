"""
102shows.Drivers
(c) 2016 Simon Leiner

This module contains the drivers for the LED strips
"""
from abc import ABCMeta, abstractmethod
import logging as log

__all__ = ['apa102', 'dummy']
__drivers__ = ['Dummy', 'APA102']


class LEDStrip(metaclass=ABCMeta):
    """
    This class provides the general interface for LED drivers that the lightshows use.
    All LED drivers for 102shows should inherit this class.
    The following restrictions apply:
        - pixel order is r,g,b
        - pixel resolution (number of dim-steps per color component) is 8-bit, so 0 - 255
    """

    def __init__(self, num_leds: int, max_clock_speed_hz: int = 4000000, initial_brightness: int = 100):
        """
        stores the given parameters and initializes the color and brightness buffers
        drivers should extend this method

        :param num_leds: number of LEDs in the strip
        :param max_clock_speed_hz: maximum clock speed (Hz) of the bus
        :param initial_brightness: initial brightness for the whole strip (to be used in child classes)
        :param multiprocessing: will this object be accessed by multiple processes?
        """
        # store the given parameters
        self.num_leds = num_leds
        self.max_clock_speed_hz = max_clock_speed_hz

        # private variables
        self.__frozen = False

    def freeze(self):
        """
        freezes the strip. All state-changing methods (__set_pixel() and __set_brightness())
        will not do anything anymore and leave the buffer unchanged
        """
        self.__frozen = True

    def unfreeze(self):
        """ revokes all effects of freeze() """
        self.__frozen = False

    @abstractmethod
    def get_pixel(self, led_num):
        """
        gets the pixel at index led_num

        :param led_num: the index of the pixel you want to get
        :return: (red, green, blue) tuple
        """

        pass

    def set_pixel(self, led_num, red, green, blue) -> None:
        """
        subclasses should not inherit this method!
        calls __set_pixel() if not frozen
        """

        if not self.__frozen:
            self.__set_pixel(led_num, red, green, blue)

    @abstractmethod
    def __set_pixel(self, led_num, red, green, blue) -> None:
        """
        Changes the pixel led_num to red, green, blue IN THE BUFFER!
        To send the buffer to the strip and show the changes, invoke strip.show()

        :param led_num: index of the RGB pixel to be changed
        :param red: red component of the pixel
        :param green: green component of the pixel
        :param blue: blue component of the pixel
        :return: none
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
    def color_tuple_to_bytes(red: int, green: int, blue: int) -> int:
        """
        converts an RGB color tuple into a 3-byte color value

        :param red: red component of the tuple
        :param green: green component of the tuple
        :param blue: blue component of the tuple
        :return: the tuple components are joined into a 3-byte value with each byte representing a color component
        """
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

    @abstractmethod
    def rotate(self, positions=1):
        """
        Treating the internal leds array as a circular buffer, rotate it by the specified number of positions.
        The number could be negative, which means rotating in the opposite direction.

        :param positions: rotate by how many steps
        :return: none
        """
        pass

    def set_brightness(self, led_num: int, brightness: int) -> None:
        """
        subclasses should not inherit this method!
        calls __set_brightness() if not frozen
        """
        if not self.__frozen:
            self.__set_brightness(led_num, brightness)

    @abstractmethod
    def __set_brightness(self, led_num: int, brightness: int) -> None:
        """
        sets the brightness for a single LED in the strip

        :param led_num: the target LED index
        :param brightness: the desired brightness (0 - 100)
        :return: none
        """
        pass

    def set_global_brightness(self, brightness: int) -> None:
        """
        calls set_brightness() for all LEDs in the strip

        :param brightness: the brightness (0 - 100) to be set all over the strip
        :return:
        """
        for led_num in range(self.num_leds):
            self.set_brightness(led_num, brightness)

    def clear_buffer(self) -> None:
        """
        sets all pixels in the color buffer to (0,0,0)

        :return: none
        """
        for led_num in range(self.num_leds):
            self.set_pixel(led_num, 0, 0, 0)

    def clear_strip(self) -> None:
        """
        clears the color buffer, then invokes a blackout on the strip by calling show()

        :return: none
        """
        self.clear_buffer()
        self.show()

    @abstractmethod
    def sync_up(self) -> None:
        """ copies the local SPI buffer to a shared object so other processes can see the current strip state """
        pass

    @abstractmethod
    def sync_down(self) -> None:
        """ applies the shared buffer to the local SPI buffer """
        pass
