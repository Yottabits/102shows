"""
SolidColor
(c) 2016 Simon Leiner

The whole strip shines in the same color.

Parameters:
   =====================================================================
   ||                     ||    python     ||   JSON representation   ||
   ||       color:        ||   3x1 tuple   ||       3x1 array         ||
   =====================================================================
"""

from lightshows.templates.base import *
from lightshows.utilities.general import blend_whole_strip_to_color, is_rgb_color_tuple
from lightshows.utilities import verifyparameters as verify


class SolidColor(Lightshow):
    def run(self):
        blend_whole_strip_to_color(self.strip, self.color)

    def init_parameters(self):
        self.color = None

    def set_parameter(self, param_name: str, value):
        if param_name == "color":
            verify.numeric(value, param_name)
            self.color = value
        else:
            InvalidParameters.unknown(param_name)

    def check_runnable(self):
        if not self.color:
            raise InvalidParameters.missing("color")
