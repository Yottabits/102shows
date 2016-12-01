"""
Two Color Blend
(c) 2016 Simon Leiner

linear transition between two colors across the strip

Parameters:
   =====================================================================
   ||                     ||    python     ||   JSON representation   ||
   || color1:             ||   3x1 tuple   ||       3x1 array         ||
   || color2:             ||   3x1 tuple   ||       3x1 array         ||
   =====================================================================
"""

from drivers.apa102 import APA102
from DefaultConfig import Configuration
import lightshows.utilities as util
import logging as log

necessary_parameters = ['color1', 'color2']

minimal_number_of_leds = 2  # you need at least 10 leds for this show


def run(strip: APA102, conf: Configuration, parameters: dict):
    # check if we have enough LEDs
    global minimal_number_of_leds
    if strip.numLEDs < minimal_number_of_leds:
        log.critical("This show needs a strip of at least {} LEDs to run correctly".format(minimal_number_of_leds))
        return

    parameters = prepare_parameters(parameters)

    transition = util.SmoothBlend(strip)

    for led in range(strip.numLEDs):
        normal_distance = led / (strip.numLEDs - 1)
        component1 = util.linear_dim(parameters["color1"], 1 - normal_distance)
        component2 = util.linear_dim(parameters["color2"], normal_distance)
        led_color = util.add_tuples(component1, component2)
        transition.set_pixel(led, *led_color)
    transition.blend()


def parameters_valid(parameters: dict):
    parameters = prepare_parameters(parameters)
    # are all necessary parameters there?
    for p in parameters:
        if p not in necessary_parameters:
            log.debug("Missing parameter {param_name}".format(param_name=p))
            return False
            # type checking
        if not util.is_rgb_color_tuple(parameters[p]):
            log.debug("{param_name} is not valid!".format(param_name=p))
            return False
    # else
    return True


def prepare_parameters(parameters: dict) -> dict:
    for p in parameters:
        if type(parameters[p]) is list:  # cast arrays to lists
            parameters[p] = tuple(parameters[p])
            log.debug("{}: {}".format(p, parameters[p]))
    return parameters
