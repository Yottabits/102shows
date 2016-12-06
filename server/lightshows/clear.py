"""
clear

This lightshow just turns the whole strip off.

Parameters:
   =====================================================================
   ||                     ||    python     ||   JSON representation   ||
   || fadetime_sec:       ||    numeric    ||        numeric          ||
   =====================================================================
"""

from lightshows.templates.base import *
from lightshows.utilities import verifyparameters as verify
from lightshows.utilities.general import blend_whole_strip_to_color
from lightshows.utilities.verifyparameters import InvalidStrip, InvalidParameters


class Clear(Lightshow):
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
        self.strip.clearStrip()
        self.strip.clearStrip()  # just to be sure

    def check_runnable(self):
        # do we have at least one LED?
        if self.strip.numLEDs < 1:
            raise InvalidStrip("This show needs a strip of at least {} LEDs to run!".format(self.strip.numLEDs))
