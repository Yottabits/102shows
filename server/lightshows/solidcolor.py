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

from lightshows.metashow import Lightshow
from lightshows.utilities import blend_whole_strip_to_color


class SolidColor(Lightshow):
    def check_runnable(self) -> bool:
        if "color" in self.parameters:
            if len(self.parameters["color"]) is 3:
                return True

        return False

    def run(self):
        blend_whole_strip_to_color(self.strip, self.parameters["color"])
