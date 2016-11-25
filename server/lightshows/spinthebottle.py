"""
SpinTheBottle
(c) 2016 Simon Leiner

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

from drivers.fake_apa102 import APA102
from DefaultConfig import Configuration
import lightshows.solidcolor
import lightshows.utilities as util
import random
from time import sleep
import logging as log

color_parameters = ['highlight_color', 'background_color']
necessary_parameters = color_parameters + ['time_sec', 'fadeout']


def run(strip: APA102, conf: Configuration, parameters: dict):
    show = SpinTheBottle(strip)

    parameters = prepare_parameters(parameters)
    show.highlight_color = parameters["highlight_color"]
    show.background_color = parameters["background_color"]

    lightshows.solidcolor.blend_to_color(strip, show.background_color)  # fade to background_color
    show.run(parameters["time_sec"], parameters["fadeout"])  # start the real show :-)


def parameters_valid(parameters: dict) -> bool:
    # prepare all types
    parameters = prepare_parameters(parameters)

    # are all necessary parameters there?
    for p in necessary_parameters:
        if p not in parameters:
            log.debug("Missing parameter {param_name}".format(param_name=p))
            return False

    # type checking
    for p in color_parameters:
        if not util.is_rgb_color_tuple(parameters[p]):
            log.debug("{param_name} is not valid!".format(param_name=p))
            return False

    time_type = type(parameters['time_sec'])
    if not (time_type is int or time_type is float):
        log.debug("Parameter time_sec is not a numeric type!")
        return False

    if not type(parameters['fadeout']) is bool:
        log.debug("Parameter fadeout is not a bool type!")
        return False

    # or else:
    return True


def prepare_parameters(parameters: dict) -> dict:
    for p in color_parameters:
        if type(parameters[p]) is list:  # cast arrays to lists
            parameters[p] = tuple(parameters[p])
    return parameters


class SpinTheBottle:
    def __init__(self, strip: APA102):
        self.strip = strip
        self.highlight_color = (200, 100, 0)
        self.highlight_sections = 72
        self.background_color = (0, 0, 0)
        self.lower_border = 0
        self.upper_border = self.strip.numLEDs

    def highlight(self, position: int, highlight_radius: int = 3):
        for led in range(0, self.strip.numLEDs):
            distance = abs(led - position)  # distance to highlight center
            if distance <= highlight_radius:
                dim_factor = (1 - (distance / highlight_radius)) ** 2
                color = util.linear_dim(self.highlight_color, dim_factor)
                self.strip.setPixel(led, *color)
            else:
                self.strip.setPixel(led, *self.background_color)
        self.strip.show()

    def run(self, time_sec: float = 5, fadeout: bool = False):
        section_width = (self.upper_border - self.lower_border) // self.highlight_sections
        target_led = random.randrange(self.lower_border, self.upper_border, section_width)
        frame_time = time_sec / (3 * self.highlight_sections)  # 3 for the three roundtrips

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
            relative_distance = abs(led - target_led) / self.strip.numLEDs
            sleep(0.0006 * time_sec / relative_distance)  # slow down a little
        self.highlight(target_led, highlight_radius=section_width // 2)

        if fadeout:
            sleep(10)
            lightshows.solidcolor.blend_to_color(self.strip, self.background_color)  # fadeout the spot
