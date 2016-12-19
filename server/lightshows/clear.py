"""
Clear
(c) 2016 Simon Leiner
licensed under the GNU Public License, version 2
"""

from helpers.color import blend_whole_strip_to_color
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
        self.register('fadetime_sec', 1, verify.not_negative_numeric)

    def run(self):
        blend_whole_strip_to_color(self.strip, (0, 0, 0), self.p['fadetime_sec'])  # fadeout
        self.strip.clear_strip()
        self.strip.clear_strip()  # just to be sure

    def check_runnable(self):
        # do we have at least one LED?
        if self.strip.num_leds < 1:
            raise InvalidStrip("This show needs a strip of at least {} LEDs to run!".format(self.strip.num_leds))
