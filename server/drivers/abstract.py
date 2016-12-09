"""
Abstract Driver
(c) Simon Leiner 2016
"""

from abc import ABCMeta, abstractmethod
from multiprocessing import Array as SharedArray

from lightshows.utilities import verifyparameters as verify


class LEDStrip(metaclass=ABCMeta):
    """
    This class provides the general interface for LED drivers that the lightshows use.
    All LED drivers for 102shows should inherit this class.
    The following restrictions apply:
        - pixel order is r,g,b
        - pixel resolution (number of dim-steps per color component) is 8-bit, so 0 - 255
    """

    def __init__(self, num_leds: int, max_clock_speed_hz: int, multiprocessing: bool = True):
        """
        stores the given parameters and initializes the color and brightness buffers

        :param num_leds: number of LEDs in the strip
        :param max_clock_speed_hz: maximum clock speed (Hz) of the bus
        :param multiprocessing: will this object be accessed by multiple processes?
        """
        # store the given parameters
        self.num_leds = num_leds
        self.max_clock_speed_hz = max_clock_speed_hz
        self.multiprocessing = multiprocessing

        # initialize the color and brightness buffers
        if self.multiprocessing:
            self.__color_buffer = SharedColorBuffer(size=self.num_leds)  # SharedColorBuffer initializes with (0,0,0)s
            self.__brightness_buffer = SharedArray('i', [100] * self.num_leds)  # full brightness
        else:
            self.__color_buffer = [(0, 0, 0)] * self.num_leds  # these two definitions are (in the view of class members
            self.__brightness_buffer = [100] * self.num_leds  # ... equivalent to the two definitions above

    @abstractmethod
    def initialize_strip_connection(self):
        """ in child classes, the strip connection should be established here """
        pass

    @property
    def color_buffer(self):
        return self.__color_buffer

    @color_buffer.setter
    def color_buffer(self, new_buffer):
        for led_num in range(self.num_leds):
            self.__color_buffer[led_num] = new_buffer[led_num]

    @property
    def brightness_buffer(self):
        return self.__brightness_buffer

    @brightness_buffer.setter
    def brightness_buffer(self, new_buffer):
        for led_num in range(self.num_leds):
            self.__brightness_buffer[led_num] = new_buffer[led_num]

    def get_pixel(self, led_num):
        """
        gets the pixel at index led_num

        :param led_num: the index of the pixel you want to get
        :return: (red, green, blue) tuple
        """
        return self.color_buffer[led_num]

    def set_pixel(self, led_num, red, green, blue) -> None:
        """
        Changes the pixel led_num to red, green, blue IN THE BUFFER!
        To send the buffer to the strip and show the changes, invoke strip.show()

        :param led_num: index of the RGB pixel to be changed
        :param red: red component of the pixel
        :param green: green component of the pixel
        :param blue: blue component of the pixel
        :return: none
        """
        if led_num < 0:
            raise IndexError("led_num cannot be < 0!")
        if led_num >= self.num_leds:
            raise IndexError("led_num is out of bounds!")
        verify.rgb_color_tuple((red, green, blue))
        self.color_buffer[led_num] = (red, green, blue)

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

    def rotate(self, positions=1):
        """
        Treating the internal leds array as a circular buffer, rotate it by the specified number of positions.
        The number could be negative, which means rotating in the opposite direction.

        :param positions: rotate by how many steps
        :return: none
        """
        cutoff = 4 * (positions % self.num_leds)
        self.color_buffer = self.color_buffer[cutoff:] + self.color_buffer[:cutoff]

    def set_brightness(self, led_num: int, brightness: int) -> None:
        """
        sets the brightness for a single LED in the strip

        :param led_num: the target LED index
        :param brightness: the desired brightness (0 - 100)
        :return: none
        """
        verify.integer(brightness, "brightness", minimum=0, maximum=100)
        self.brightness_buffer[led_num] = brightness

    def set_global_brightness(self, brightness: int) -> None:
        """
        calls set_brightness() for all LEDs in the strip

        :param brightness: the brightness (0 - 100) to be set all over the strip
        :return:
        """
        for led_num in range(self.num_leds):
            self.set_brightness(led_num, brightness)

    def clear_color_buffer(self) -> None:
        """
        sets all pixels in the color buffer to (0,0,0)

        :return: none
        """
        self.color_buffer = [(0, 0, 0)] * self.num_leds

    def clear_strip(self) -> None:
        """
        clears the color buffer, then invokes a blackout on the strip by calling show()

        :return: none
        """
        self.clear_color_buffer()
        self.show()


class SharedColorBuffer:
    """
    A static array that stores integer triplets.
    """

    def __init__(self, size: int):
        self.__r = SharedArray('i', [0, ] * size)
        self.__g = SharedArray('i', [0, ] * size)
        self.__b = SharedArray('i', [0, ] * size)

    def __getitem__(self, key: int):
        return self.__r[key], self.__g[key], self.__b[key]

    def __setitem__(self, key: int, value: tuple) -> None:
        r, g, b = value
        self.__r[key] = r
        self.__g[key] = g
        self.__b[key] = b
