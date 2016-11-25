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

import drivers.fake_apa102 as APA102
from DefaultConfig import Configuration
import lightshows.utilities as util


def run(strip: APA102, conf: Configuration, parameters: dict):
    blend_to_color(strip, parameters["color"])


def blend_to_color(strip: APA102, color: tuple, fadetime_sec: int = 2):
    transition = util.SmoothBlend(strip)
    transition.set_color_for_whole_strip(*color)
    transition.blend(time_sec=fadetime_sec)


def parameters_valid(parameters: dict) -> bool:
    if "color" in parameters:
        if len(parameters["color"]) is 3:
            return True

    return False
