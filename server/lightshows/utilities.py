"""
utilities

This class provides helper functions and classes for the lightshows:
    - linear_dim(undimmed, factor)
    - is_rgb_color_tuple(to_check)
    - add_tuples(tuple1, tuple2)

    - SmoothBlend
    - MeasureFPS
"""
import time
from drivers.fake_apa102 import APA102
import types
import logging as log


def linear_dim(undimmed: tuple, factor: float) -> tuple:
    """ multiply all components of :param undimmed with :param factor
    :return: resulting vector, as int
    """
    dimmed = ()
    for i in undimmed:
        i = int(factor * i)  # brightness needs to be an integer
        dimmed = dimmed + (i,)  # merge tuples
    return dimmed


def is_rgb_color_tuple(to_check) -> bool:
    """ check if :param to_check is a rgb color tuple"""
    if type(to_check) is not tuple:
        return False

    if len(to_check) is not 3:  # an rgb tuple has three components
        return False

    for component in to_check:
        if type(component) is not int:
            return False
        if not (0 <= component <= 255):
            return False

    # if no break condition is met:
    return True


def add_tuples(tuple1: tuple, tuple2: tuple):
    """add :param tuple1 component-wise to :param tuple2"""
    if len(tuple1) is not len(tuple2):
        return None  # this type of addition is not defined for tuples with different lengths
    # calculate sum
    sum_of_two = []
    for i in range(len(tuple1)):
        sum_of_two.append(tuple1[i] + tuple2[i])
    return tuple(sum_of_two)


class MeasureFPS:
    """ measures the refresh rate available to the strip"""

    def __init__(self, strip: APA102):
        self.strip = strip
        self.active_color = (255, 255, 255)
        self.passed_color = (0, 100, 100)

    def run(self) -> float:
        """runs a test on the LED strip framerate
        :return: a tuple with (framerate, time_elapsed, number_of_frames)
        """
        self.strip.clearStrip()
        self.strip.clearStrip()  # just to be sure ;)

        start_time = time.perf_counter()
        for led in range(0, self.strip.numLEDs):
            self.strip.setPixel(led, *self.active_color)
            self.strip.show()
            self.strip.setPixel(led, *self.passed_color)
        stop_time = time.perf_counter()

        time_elapsed = stop_time - start_time
        number_of_frames = self.strip.numLEDs
        framerate = number_of_frames / time_elapsed

        time.sleep(1)
        self.strip.clearStrip()
        self.strip.clearStrip()

        return (framerate, time_elapsed, number_of_frames)


class SmoothBlend:
    """
    SmoothBlend

    This class lets the user define a specific state of the strip (=> target_colors) and then smoothly blends the
    current state over to the set state.

    It provides the following functions:
        - set_pixel(ledNum, red, green, blue)
        - set_color_for_whole_strip(red, green, blue)
        - blend(time_sec, blend_function)

    """

    def __init__(self, strip: APA102):
        self.strip = strip
        self.target_colors = [(0, 0, 0)] * self.strip.numLEDs  # an array of tuples

    def set_pixel(self, ledNum: int, red: int, green: int, blue: int):
        """ set the desired state of a given pixel after the blending is finished """
        # check if the given color values are valid
        for component in (red, green, blue):
            if type(component) is not int:
                log.warning("RGB value for pixel {num} is not an integer!".format(num=ledNum))
                return
            if component < 0 or component > 255:
                log.warning("RGB value for pixel {num} is out of bounds! (0-255)".format(num=ledNum))
                return

        # store in buffer
        self.target_colors[ledNum] = (red, green, blue)

    def set_color_for_whole_strip(self, red: int, green: int, blue: int):
        """ set the same color for all LEDs in the strip """
        for ledNum in range(self.strip.numLEDs):
            self.set_pixel(ledNum, red, green, blue)

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
        for ledNum in range(self.strip.numLEDs):
            initial_colors.append(self.strip.getPixel(ledNum))

        # do the actual fadeout
        now = time.perf_counter()
        end_time = time.perf_counter() + time_sec
        while now < end_time:
            fade_progress = (end_time - now) / time_sec
            for ledNum in range(self.strip.numLEDs):
                color = blend_function(initial_colors[ledNum], self.target_colors[ledNum], fade_progress)
                self.strip.setPixel(ledNum, *color)
            self.strip.show()
            now = time.perf_counter()

        # set to final target state
        for ledNum in range(self.strip.numLEDs):
            self.strip.setPixel(ledNum, *(self.target_colors[ledNum]))
