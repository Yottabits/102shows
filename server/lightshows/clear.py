"""
clear

This lightshow just turns the whole strip off.

Parameters:
   =====================================================================
   ||                     ||    python     ||   JSON representation   ||
   || fadetime_sec:       ||    numeric    ||        numeric          ||
   =====================================================================
"""

from drivers.fake_apa102 import APA102
import lightshows.solidcolor
from DefaultConfig import Configuration


# run this "show"
def run(strip: APA102, conf: Configuration, parameters: dict):
    fadetime_sec = parameters["fadetime_sec"]

    if fadetime_sec > 0:
        lightshows.solidcolor.blend_to_color(strip, (0, 0, 0), fadetime_sec)  # fadeout
    strip.clearStrip()


# tolerate no parameters
def parameters_valid(parameters: dict) -> bool:
    # is "fadetime_sec" set?
    if "fadetime_sec" not in parameters:
        return False

    # is "fadetime_sec" numeric?
    param_type = type(parameters["fadetime_sec"])
    if not (param_type is int or param_type is float):
        return False

    # is "fadetime_sec" positive?
    if parameters["fadetime_sec"] < 0:
        return False

    # now everything seems alright
    return True
