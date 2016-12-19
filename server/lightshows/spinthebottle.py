"""
SpinTheBottle
(c) 2016 Simon Leiner
licensed under the GNU Public License, version 2
"""

import random

from helpers.color import blend_whole_strip_to_color, linear_dim
from helpers.preprocessors import list_to_tuple
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

    def init_parameters(self):
        # MQTT-settable
        self.register('highlight_color', None, verify.rgb_color_tuple, preprocessor=list_to_tuple)
        self.register('background_color', None, verify.rgb_color_tuple, preprocessor=list_to_tuple)
        self.register('time_sec', None, verify.positive_numeric)
        self.register('fadeout', None, verify.boolean)

        # private
        self.lower_border = 0
        self.upper_border = self.strip.num_leds - 1
        self.highlight_sections = 72

    def check_runnable(self):
        # do we have enough LEDs
        if self.strip.num_leds < self.minimal_number_of_leds:
            InvalidStrip("This show needs a strip of at last {} LEDs to run correctly!".format(
                self.minimal_number_of_leds))

        # do we have all necessary parameters?
        necessary_parameters = [(self.p['highlight_color'], "highlight_color"),
                                (self.p['background_color'], "background_color"),
                                (self.p['time_sec'], "time_sec"),
                                (self.p['fadeout'], "fadeout")]
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
                color = linear_dim(self.p['highlight_color'], dim_factor)
                self.strip.set_pixel(led, *color)
            else:
                self.strip.set_pixel(led, *self.p['background_color'])
        self.strip.show()

    def run(self):
        section_width = (self.upper_border - self.lower_border) // self.highlight_sections
        target_led = random.randrange(self.lower_border, self.upper_border, section_width)
        frame_time = self.p['time_sec'] / (3 * self.highlight_sections)  # 3 for the three roundtrips

        # go round the strip one time
        for led in range(self.lower_border, self.upper_border + 1, section_width):
            self.highlight(led, highlight_radius=section_width // 2)
            self.sleep(frame_time)
        for led in range(self.upper_border + 1, self.lower_border, -section_width):
            self.highlight(led, highlight_radius=section_width // 2)
            self.sleep(frame_time)

        # focus on target
        for led in range(self.lower_border, target_led, section_width):
            self.highlight(led)
            relative_distance = abs(led - target_led) / self.strip.num_leds
            self.sleep(0.0006 * self.p['time_sec'] / relative_distance)  # slow down a little
        self.highlight(target_led, highlight_radius=section_width // 2)

        if self.p['fadeout']:
            self.sleep(10)
            blend_whole_strip_to_color(self.strip, self.p['background_color'])  # fadeout the spot
