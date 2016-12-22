"""
Color Helpers
(c) 2016 Simon Leiner
licensed under the GNU Public License, version 2

This class provides helper functions and classes for the lightshows:
    - grayscale_correction(lightness, max_in, max_out)
    - linear_dim(undimmed, factor)
    - is_rgb_color_tuple(to_check)
    - add_tuples(tuple1, tuple2)
    - blend_whole_strip_to_color(strip, color, fadetime_sec)
    - wheel(wheel_pos)

    - SmoothBlend
"""

import types
import logging
import time

from drivers import LEDStrip
from helpers import verify, exceptions


def grayscale_correction(lightness: float, max_in: float = 255.0, max_out: int = 255):
    """
    correct the non-linear human perception of the led brightness according to CIE 1931
    This is commonly mistaken for gamma correction. For more information, read here: https://goo.gl/9Ji129

    :param lightness: linear brightness value between 0 and max_in
    :param max_in: maximum value for lightness
    :param max_out: maximum output integer value (255 for 8-bit LED drivers)
    :return the correct PWM duty cycle for humans to see the desired lightness as integer
    """

    # safeguard and shortcut
    if lightness <= 0:
        return 0
    elif lightness >= max_in:
        return max_out

    # lightness correction: https://en.wikipedia.org/wiki/Lab_color_space#Reverse_transformation
    # the formula is:
    #                 Y = Y_max * g( ( L* + 16) /  116 ) with L* being the lightness between 0 and 100
    #
    #        with  g(t) = > 3 * delta^2 * ( t - 4/29)    for t ≤ delta
    #                     > t^3                          for t > delta      where delta = 6/29
    #
    # this can be simplified to:
    #                 Y = > (L* / 902.33)          for L* ≤ 8
    #                     > ((L* + 16) / 116)^3    for L* > 8
    #
    # here the ranges are still 0...Y...1 and 0...L*...100

    l_star = lightness / max_in * 100  # map from 0..max_in to 0..100

    if l_star <= 8:
        duty_cycle = l_star / 902.33
    else:
        duty_cycle = ((l_star + 16) / 116) ** 3

    return round(duty_cycle * max_out)  # this will be an integer!


def wheel(wheel_pos: float):
    """
    Get a color from a color wheel: Green -> Red -> Blue -> Green

    :param wheel_pos: numeric from 0 to 254
    :return: RGB color tuple
    """

    if wheel_pos > 254:
        wheel_pos = 254  # Safeguard
    if wheel_pos < 85:  # Green -> Red
        color = (wheel_pos * 3, 255 - wheel_pos * 3, 0)
    elif wheel_pos < 170:  # Red -> Blue
        wheel_pos -= 85
        color = (255 - wheel_pos * 3, 0, wheel_pos * 3)
    else:  # Blue -> Green
        wheel_pos -= 170
        color = (0, wheel_pos * 3, 255 - wheel_pos * 3)

    return color


def linear_dim(undimmed: tuple, factor: float) -> tuple:
    """
    multiply all components of undimmed with factor

    :param undimmed: the vector
    :param factor: the factor to multiply the components of the vector byy
    :return: resulting RGB color vector
    """
    dimmed = ()
    for i in undimmed:
        i *= factor
        dimmed += i,  # merge tuples
    return dimmed


def add_tuples(tuple1: tuple, tuple2: tuple):
    """
    add two tuples component-wise

    :param tuple1: summand
    :param tuple2: summand
    :return: sum
    """

    if len(tuple1) is not len(tuple2):
        return None  # this type of addition is not defined for tuples with different lengths
    # calculate sum
    sum_of_two = []
    for i in range(len(tuple1)):
        sum_of_two.append(tuple1[i] + tuple2[i])
    return tuple(sum_of_two)


class SmoothBlend:
    """
    SmoothBlend

    This class lets the user define a specific state of the strip (=> target_colors) and then smoothly blends the
    current state over to the set state.

    It provides the following functions:
        - set_pixel(led_num, red, green, blue)
        - set_color_for_whole_strip(red, green, blue)
        - blend(time_sec, blend_function)

    """

    logger = logging.getLogger('102shows.server.helpers.color.SmoothBlend')

    def __init__(self, strip: LEDStrip):
        self.strip = strip
        self.target_colors = [(0.0, 0.0, 0.0)] * self.strip.num_leds  # an array of float tuples

    def set_pixel(self, led_num: int, red: float, green: float, blue: float):
        """ set the desired state of a given pixel after the blending is finished """
        # check if the given color values are valid
        try:
            verify.rgb_color_tuple((red, green, blue))
        except exceptions.InvalidParameters as error_message:
            self.logger.error(error_message)

        # store in buffer
        self.target_colors[led_num] = (red, green, blue)

    def set_color_for_whole_strip(self, red: float, green: float, blue: float):
        """ set the same color for all LEDs in the strip """
        for led_num in range(self.strip.num_leds):
            self.set_pixel(led_num, red, green, blue)

    class BlendFunctions:
        """
        BlendFunctions
        an internal class which provides functions to blend between two colors by a parameter fade_progress
        for fade_progress = 0 the function should return the start_color
        for fade_progress = 1 the function should return the end_color
        """

        @classmethod
        def linear_blend(cls, start_color: tuple, end_color: tuple, fade_progress: float) -> tuple:
            """ linear blend => see https://goo.gl/lG8RIW """
            return cls.power_blend(1, start_color, end_color, fade_progress)

        @classmethod
        def parabolic_blend(cls, start_color: tuple, end_color: tuple, fade_progress: float) -> tuple:
            """ quadratic blend => see https://goo.gl/hzeFb6 """
            return cls.power_blend(2, start_color, end_color, fade_progress)

        @classmethod
        def cubic_blend(cls, start_color: tuple, end_color: tuple, fade_progress: float) -> tuple:
            """ cubic blend => see https://goo.gl/wZWm07 """
            return cls.power_blend(3, start_color, end_color, fade_progress)

        @classmethod
        def power_blend(cls, power: float, start_color: tuple, end_color: tuple, fade_progress: float) -> tuple:
            """ blend two colors using a power function, the exponent is set via :param power """
            start_component = linear_dim(start_color, fade_progress ** power)
            target_component = linear_dim(end_color, (1 - fade_progress) ** power)
            return add_tuples(start_component, target_component)

    def blend(self, time_sec: float = 2, blend_function: types.FunctionType = BlendFunctions.linear_blend):
        """ blend the current LED state to the desired state """
        # buffer current status
        initial_colors = []
        for led_num in range(self.strip.num_leds):
            initial_colors.append(self.strip.get_pixel(led_num))

        # do the actual fadeout
        now = time.perf_counter()
        end_time = time.perf_counter() + time_sec
        while now < end_time:
            fade_progress = (end_time - now) / time_sec
            for led_num in range(self.strip.num_leds):
                color = blend_function(initial_colors[led_num], self.target_colors[led_num], fade_progress)
                self.strip.set_pixel(led_num, *color)
            self.strip.show()
            now = time.perf_counter()

        # set to final target state
        for led_num in range(self.strip.num_leds):
            self.strip.set_pixel(led_num, *(self.target_colors[led_num]))
        self.strip.show()


def blend_whole_strip_to_color(strip: LEDStrip, color: tuple, fadetime_sec: float = 2) -> None:
    """
    this name is pretty self-explanatory ;-)

    :param strip: LEDStrip object
    :param color: the color to blend two
    :param fadetime_sec: the time in seconds to blend in
    """
    transition = SmoothBlend(strip)
    transition.set_color_for_whole_strip(*color)
    transition.blend(time_sec=fadetime_sec)
