"""
Two Color Blend
(c) 2016 Simon Leiner
licensed under the GNU Public License, version 2
"""

from helpers.color import SmoothBlend, linear_dim, add_tuples
from helpers.preprocessors import list_to_tuple
from lightshows.templates.base import *


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

    def init_parameters(self):
        self.register('color1', None, verify.rgb_color_tuple, preprocessor=list_to_tuple)
        self.register('color2', None, verify.rgb_color_tuple, preprocessor=list_to_tuple)

    def check_runnable(self):
        # do we have all parameters
        if self.p['color1'] is None:
            raise InvalidParameters.missing("color1")
        if self.p['color2'] is None:
            raise InvalidParameters.missing("color2")

    def run(self):
        transition = SmoothBlend(self.strip)

        for led in range(self.strip.num_leds):
            normal_distance = led / (self.strip.num_leds - 1)
            component1 = linear_dim(self.p['color1'], 1 - normal_distance)
            component2 = linear_dim(self.p['color2'], normal_distance)
            led_color = add_tuples(component1, component2)
            transition.set_pixel(led, *led_color)
        transition.blend()
