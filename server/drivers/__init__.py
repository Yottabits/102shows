# 102shows Drivers
# (c) 2016-2017 Simon Leiner
# licensed under the GNU Public License, version 2

"""This module contains the drivers for the LED strips"""

import logging
from abc import ABCMeta, abstractmethod
from multiprocessing import Array as SyncedArray
from multiprocessing import Value as SyncedValue

__all__ = ['apa102', 'dummy', 'LEDStrip']

logger = logging.getLogger('102shows.drivers')


class LEDStrip(metaclass=ABCMeta):
    """\
    This class provides the general interface for LED drivers that the lightshows use.
    All LED drivers for 102shows should inherit this class.
    Mind the following:

        - Pixel order is ``r,g,b``
        - Pixel resolution (number of dim-steps per color component) is 8-bit, so minimum brightness is ``0``
          and maximum brightness is ``255``

    The constructor stores the given parameters and initializes the color and brightness buffers.
    Drivers can and should extend this method.

    :param num_leds: number of LEDs in the strip
    :param max_clock_speed_hz: maximum clock speed (Hz) of the bus
    """

    def __init__(self, num_leds: int, max_clock_speed_hz: int = 4000000, max_global_brightness: float = 1.0):
        # store the given parameters
        self.num_leds = num_leds
        self.max_clock_speed_hz = max_clock_speed_hz

        # private variables
        self.__is_frozen = False
        self._global_brightness = 1.0  #: global brightness multiplicator (0-1)
        self.__max_global_brightness = max_global_brightness

        # buffers
        self.color_buffer = [(0.0, 0.0, 0.0)] * self.num_leds
        self.brightness_buffer = [1.0] * self.num_leds
        #: the individual dim factors for each LED (0-1), EXCLUDING the global dim factor

        self.synced_red_buffer = SyncedArray('f', [0.0] * self.num_leds)
        self.synced_green_buffer = SyncedArray('f', [0.0] * self.num_leds)
        self.synced_blue_buffer = SyncedArray('f', [0.0] * self.num_leds)
        self.synced_brightness_buffer = SyncedArray('f', self.brightness_buffer)
        self.synced_global_brightness = SyncedValue('f', self._global_brightness)

    def __del__(self):
        """Invokes :py:func': `close` and deletes all the buffers."""
        self.close()

        del self.color_buffer, self.synced_red_buffer, self.synced_green_buffer, self.synced_blue_buffer
        del self.brightness_buffer, self.synced_brightness_buffer

        logger.info("Driver successfully closed")

    @property
    def __frozen(self):
        """\
        determines if the strip state can be altered using the :py:func:`set_pixel` function or the brightness setters
        """
        return self.__is_frozen

    @__frozen.setter
    def __frozen(self, value):
        self.__is_frozen = value

        if self.__is_frozen:
            logger.debug("Strip is FREEZED")
        else:
            logger.debug("Strip is NOT FREEZED")

    max_refresh_time_sec = 1
    """\
    The maximum time (in *seconds*) that a call of :func:`show` needs to execute.
    Currently only used in :func:`lightshows.templates.base.sleep`
    """

    @abstractmethod
    def close(self) -> None:
        """\
        **An abstract method to be overwritten by the drivers.**

        It should close the bus connection and clean up any remains.
        """
        pass

    def freeze(self) -> None:
        """\
        Freezes the strip.
        All state-changing methods (:func:`on_color_change` and :func:`on_brightness_change`)
        must not do anything anymore and leave the buffer unchanged.
        """
        self.__frozen = True

    def unfreeze(self) -> None:
        """Revokes all effects of :func:`freeze`"""
        self.__frozen = False

    def get_pixel(self, led_num: int) -> tuple:
        """\
        Returns the pixel at index ``led_num``

        :param led_num: the index of the pixel you want to get
        :return: ``(red, green, blue)`` as tuple
        """

        return self.color_buffer[led_num]

    # do not overwrite this method:
    def set_pixel(self, led_num: int, red: float, green: float, blue: float) -> None:
        """\
        The buffer value of pixel ``led_num`` is set to ``(red, green, blue)``

        :param led_num: index of the pixel to be set
        :param red: red component of the pixel (``0.0 - 255.0``)
        :param green: green component of the pixel (``0.0 - 255.0``)
        :param blue: blue component of the pixel (``0.0 - 255.0``)
        """

        if led_num < 0:
            return  # Pixel is invisible, so ignore
        if led_num >= self.num_leds:
            return  # again, invisible

        if not self.__frozen:
            self.color_buffer[led_num] = (red, green, blue)
            self.on_color_change(led_num, red, green, blue)

    @abstractmethod
    def on_color_change(self, led_num, red: float, green: float, blue: float) -> None:
        """\
        Changes the message buffer after a pixel was changed in the global color buffer.
        To send the buffer to the strip and show the changes, you must invoke :func:`show`

        :param led_num: index of the pixel to be set
        :param red: red component of the pixel (``0.0 - 255.0``)
        :param green: green component of the pixel (``0.0 - 255.0``)
        :param blue: blue component of the pixel (``0.0 - 255.0``)
        """

    def set_pixel_bytes(self, led_num: int, rgb_color: int) -> None:
        """\
        Changes the pixel ``led_num`` to the given color **in the buffer**.
        To send the buffer to the strip and show the changes, invoke :func:`show`

        *If you do not know, how the 3-byte* ``rgb_color`` *works, just use* :func:`set_pixel` *.*

        :param led_num: index of the pixel to be set
        :param rgb_color: a 3-byte RGB color value represented as a base-10 integer
        """
        red, green, blue = self.color_bytes_to_tuple(rgb_color)
        self.set_pixel(led_num, red, green, blue)

    @staticmethod
    def color_tuple_to_bytes(red: float, green: float, blue: float) -> int:
        """\
        Converts an RGB color tuple (like ``(255, 0, 26)``) into a 3-byte color value (like ``FF001A``)

        :param red: red component of the tuple (``0.0 - 255.0``)
        :param green: green component of the tuple (``0.0 - 255.0``)
        :param blue: blue component of the tuple (``0.0 - 255.0``)
        :return: the tuple components joined into a 3-byte value with each byte representing a color component
        """

        # round to integers
        red = round(red)
        green = round(green)
        blue = round(blue)

        return (red << 16) + (green << 8) + blue

    @staticmethod
    def color_bytes_to_tuple(rgb_color: int) -> tuple:
        """\
        Converts a 3-byte color value (like ``FF001A``) into an RGB color tuple (like ``(255, 0, 26)``).

        :param rgb_color: a 3-byte RGB color value represented as a base-10 integer
        :return: color tuple ``(red, green, blue)``
        """
        r = (rgb_color & 0xFF0000) >> 16
        g = (rgb_color & 0x00FF00) >> 8
        b = rgb_color & 0x0000FF
        return r, g, b

    @abstractmethod
    def show(self) -> None:
        """\
        **Subclasses should overwrite this method**

        This method should show the buffered pixels on the strip,
        e.g. write the message buffer to the port on which the strip is connected.
        """
        pass

    def rotate(self, positions: int = 1) -> None:
        """\
        Treating the internal leds array as a circular buffer, rotate it by the specified number of positions.
        The number can be negative, which means rotating in the opposite direction.

        :param positions: the number of steps to rotate
        """
        self.color_buffer = self.color_buffer[positions:] + self.color_buffer[:positions]
        for led_num in range(self.num_leds):
            r, g, b = self.get_pixel(led_num)
            self.on_color_change(led_num, r, g, b)

    def set_brightness(self, led_num: int, brightness: float) -> None:
        """\
        Sets the brightness for a single LED in the strip.
        A global multiplier is applied.

        :param led_num: the target LED index
        :param brightness: the desired brightness (``0.0 - 1.0``)
        """

        if self.__frozen:  # skip if show is frozen
            return

        # limit brightness to the area between (and including) 0.0 and 1.0
        if brightness < 0.0:
            brightness = 0.0
        elif brightness > 1.0:
            brightness = 1.0

        self.brightness_buffer[led_num] = brightness
        self.on_brightness_change(led_num)

    @abstractmethod
    def on_brightness_change(self, led_num: int) -> None:
        """\
        Reacts to a brightness change at ``led_num`` by modifying the message buffer

        :param led_num: number of the LED whose brightness was modified
        """
        pass

    def set_global_brightness(self, brightness: float) -> None:
        """\
        Sets a global brightness multiplicator which applies to every single LED's brightness.

        :param brightness: the global brightness (``0.0 - 1.0``) multiplicator to be set
        """
        if brightness < 0.0:
            self._global_brightness = 0.0
        elif brightness > self.__max_global_brightness:
            self._global_brightness = self.__max_global_brightness
        else:
            self._global_brightness = brightness

        for led_num in range(self.num_leds):
            self.on_brightness_change(led_num)

    def clear_buffer(self) -> None:
        """Resets all pixels in the color buffer to ``(0,0,0)``."""
        for led_num in range(self.num_leds):
            self.set_pixel(led_num, 0, 0, 0)

    def clear_strip(self) -> None:
        """Clears the color buffer, then invokes a blackout on the strip by calling :py:func:`show`"""
        self.clear_buffer()
        self.show()

    def sync_up(self) -> None:
        """\
        Copies the local color and brightness buffers to the shared buffer
        so other processes can see the current strip state.
        """
        logger.info("sync_up()")

        self.synced_global_brightness.value = self._global_brightness

        for led_num, (red, green, blue) in enumerate(self.color_buffer):
            # colors
            self.synced_red_buffer[led_num] = red
            self.synced_green_buffer[led_num] = green
            self.synced_blue_buffer[led_num] = blue

            # brightness
            self.synced_brightness_buffer[led_num] = self.brightness_buffer[led_num]

    def sync_down(self) -> None:
        """Reads the shared color and brightness buffers and copies them to the local buffers"""
        logger.info("sync_down()")

        self._global_brightness = self.synced_global_brightness.value

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
