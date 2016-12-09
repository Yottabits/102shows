"""
Two Color Blend
(c) 2016 Simon Leiner
"""

from lightshows.templates.base import *
from lightshows.utilities import verifyparameters as verify
from lightshows.utilities.general import SmoothBlend, linear_dim, add_tuples
from lightshows.utilities.verifyparameters import InvalidParameters


class TwoColorBlend(Lightshow):
    """
    linear transition between two colors across the strip

    Parameters:
       =====================================================================
       ||                     ||    python     ||   JSON representation   ||
       || color1:             ||   3x1 tuple   ||       3x1 array         ||
       || color2:             ||   3x1 tuple   ||       3x1 array         ||
       =====================================================================
    """
    def run(self):
        transition = SmoothBlend(self.strip)

        for led in range(self.strip.num_leds):
            normal_distance = led / (self.strip.num_leds - 1)
            component1 = linear_dim(self.color1, 1 - normal_distance)
            component2 = linear_dim(self.color2, normal_distance)
            led_color = add_tuples(component1, component2)
            transition.set_pixel(led, *led_color)
        transition.blend()

    def init_parameters(self):
        self.color1 = None
        self.color2 = None

    def set_parameter(self, param_name: str, value):
        if type(value) is list:
            value = tuple(value)

        if param_name == "color1":
            verify.rgb_color_tuple(value, param_name)
            self.color1 = value
        elif param_name == "color2":
            verify.rgb_color_tuple(value, param_name)
            self.color2 = value
        else:
            raise InvalidParameters.unknown(param_name)

    def check_runnable(self):
        # do we have all parameters
        if self.color1 is None:
            raise InvalidParameters.missing("color1")
        if self.color2 is None:
            raise InvalidParameters.missing("color2")
