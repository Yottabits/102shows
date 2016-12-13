"""
Clear
(c) 2016 Simon Leiner
"""

from helpers.color import blend_whole_strip_to_color
from helpers.exceptions import InvalidStrip, InvalidParameters
from lightshows.templates.base import *


class Clear(Lightshow):
    """
    This lightshow just turns the whole strip off.

    Parameters:
       =====================================================================
       ||                     ||    python     ||   JSON representation   ||
       || fadetime_sec:       ||    numeric    ||        numeric          ||
       =====================================================================
    """
    def init_parameters(self):
        self.fadetime_sec = None

    def set_parameter(self, param_name: str, value):
        if param_name == "fadetime_sec":
            verify.numeric(value, param_name)
            self.fadetime_sec = value
        else:
            raise InvalidParameters.unknown(param_name)

    def run(self):
        blend_whole_strip_to_color(self.strip, (0, 0, 0), self.fadetime_sec)  # fadeout
        self.strip.clear_strip()
        self.strip.clear_strip()  # just to be sure

    def check_runnable(self):
        # do we have at least one LED?
        if self.strip.num_leds < 1:
            raise InvalidStrip("This show needs a strip of at least {} LEDs to run!".format(self.strip.num_leds))
