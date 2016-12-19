"""
SolidColor
(c) 2016 Simon Leiner
licensed under the GNU Public License, version 2
"""

from helpers.color import blend_whole_strip_to_color
from helpers.preprocessors import list_to_tuple
from lightshows.templates.base import *


class SolidColor(Lightshow):
    """
    The whole strip shines in the same color.

    Parameters:
       =====================================================================
       ||                     ||    python     ||   JSON representation   ||
       ||       color:        ||   3x1 tuple   ||       3x1 array         ||
       =====================================================================
    """

    def init_parameters(self):
        self.register('color', None, verify.rgb_color_tuple, preprocessor=list_to_tuple)

    def check_runnable(self):
        if self.p['color'] is None:
            raise InvalidParameters.missing('color')

    def run(self):
        blend_whole_strip_to_color(self.strip, self.p['color'])
