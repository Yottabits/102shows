"""
SolidColor
(c) 2016 Simon Leiner
"""

from lightshows.templates.base import *
from lightshows.utilities import verifyparameters as verify
from lightshows.utilities.general import blend_whole_strip_to_color
from lightshows.utilities.verifyparameters import InvalidParameters


class SolidColor(Lightshow):
    """
    The whole strip shines in the same color.

    Parameters:
       =====================================================================
       ||                     ||    python     ||   JSON representation   ||
       ||       color:        ||   3x1 tuple   ||       3x1 array         ||
       =====================================================================
    """
    def run(self):
        blend_whole_strip_to_color(self.strip, self.color)

    def init_parameters(self):
        self.color = None

    def set_parameter(self, param_name: str, value):
        if param_name == "color":
            if type(value) is list:
                value = tuple(value)
            verify.rgb_color_tuple(value, param_name)
            self.color = value
        else:
            InvalidParameters.unknown(param_name)

    def check_runnable(self):
        if not self.color:
            raise InvalidParameters.missing("color")
