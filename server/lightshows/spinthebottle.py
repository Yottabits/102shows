"""
SpinTheBottle
(c) 2016 Simon Leiner
"""
import random
from time import sleep

from helpers.color import blend_whole_strip_to_color, linear_dim
from helpers.exceptions import InvalidStrip, InvalidParameters
from lightshows.templates.base import *


class SpinTheBottle(Lightshow):
    """
    A light beam runs back and forth the strip and stops at a random location

    Parameters:
       =====================================================================
       ||                     ||    python     ||   JSON representation   ||
       || highlight_color:    ||   3x1 tuple   ||       3x1 array         ||
       || background_color:   ||   3x1 tuple   ||       3x1 array         ||
       || time_sec:           ||    numeric    ||        numeric          ||
       || fadeout:            ||     bool      ||          bool           ||
       =====================================================================
    """
    minimal_number_of_leds = 144

    def set_parameter(self, param_name: str, value):
        if param_name == "highlight_color":
            if type(value) is list:
                value = tuple(value)
            verify.rgb_color_tuple(value, param_name)
            self.highlight_color = value
        elif param_name == "background_color":
            if type(value) is list:
                value = tuple(value)
            verify.rgb_color_tuple(value, param_name)
            self.background_color = value
        elif param_name == "time_sec":
            verify.positive_numeric(value, param_name)
            self.time_sec = value
        elif param_name == "fadeout":
            verify.boolean(value, param_name)
            self.fadeout = value
        elif param_name == "lower_border":
            verify.integer(value, param_name, minimum=0, maximum=self.strip.num_leds - 2)
            self.lower_border = value
        elif param_name == "upper_border":
            verify.integer(value, param_name, minimum=1, maximum=self.strip.num_leds - 1)
            self.upper_border = value
        elif param_name == "highlight_sections":
            verify.integer(value, param_name, minimum=1, maximum=self.strip.num_leds)
            self.highlight_sections = value
        else:
            raise InvalidParameters.unknown(param_name)

    def init_parameters(self):
        self.highlight_color = None
        self.background_color = None
        self.time_sec = None
        self.fadeout = None

        self.lower_border = 0
        self.upper_border = self.strip.num_leds - 1
        self.highlight_sections = 72

    def check_runnable(self):
        # do we have enough LEDs
        if self.strip.num_leds < self.minimal_number_of_leds:
            InvalidStrip("This show needs a strip of at last {} LEDs to run correctly!".format(
                self.minimal_number_of_leds))
        # do we have all necessary parameters?
        necessary_parameters = [(self.highlight_color, "highlight_color"),
                                (self.background_color, "background_color"),
                                (self.time_sec, "time_sec"),
                                (self.fadeout, "fadeout")]
        for parameter, parameter_name in necessary_parameters:
            if parameter is None:
                raise InvalidParameters.missing(parameter_name)

        # is our area (limited by lower_border and upper_border) wide enough?
        led_width = self.upper_border - self.lower_border + 1
        if led_width < 2:   # with less than two LEDs there is no random choice possible
            raise InvalidParameters("\"upper_border\" (now: {}) must be greater than \"lower_border\" (now: {})".format(
                self.lower_border, self.upper_border))
        if led_width < self.highlight_sections:
            raise InvalidParameters("This show needs at least {} LEDs to run. Please modify the strip borders.".format(
                self.highlight_sections))

    def highlight(self, position: int, highlight_radius: int = 3):
        for led in range(0, self.strip.num_leds):
            distance = abs(led - position)  # distance to highlight center
            if distance <= highlight_radius:
                dim_factor = (1 - (distance / highlight_radius)) ** 2
                color = linear_dim(self.highlight_color, dim_factor)
                self.strip.set_pixel(led, *color)
            else:
                self.strip.set_pixel(led, *self.background_color)
        self.strip.show()

    def run(self):
        section_width = (self.upper_border - self.lower_border) // self.highlight_sections
        target_led = random.randrange(self.lower_border, self.upper_border, section_width)
        frame_time = self.time_sec / (3 * self.highlight_sections)  # 3 for the three roundtrips

        # go round the strip one time
        for led in range(self.lower_border, self.upper_border + 1, section_width):
            self.highlight(led, highlight_radius=section_width // 2)
            sleep(frame_time)
        for led in range(self.upper_border + 1, self.lower_border, -section_width):
            self.highlight(led, highlight_radius=section_width // 2)
            sleep(frame_time)

        # focus on target
        for led in range(self.lower_border, target_led, section_width):
            self.highlight(led)
            relative_distance = abs(led - target_led) / self.strip.num_leds
            sleep(0.0006 * self.time_sec / relative_distance)  # slow down a little
        self.highlight(target_led, highlight_radius=section_width // 2)

        if self.fadeout:
            sleep(10)
            blend_whole_strip_to_color(self.strip, self.background_color)  # fadeout the spot
