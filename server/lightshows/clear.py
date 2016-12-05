"""
clear

This lightshow just turns the whole strip off.

Parameters:
   =====================================================================
   ||                     ||    python     ||   JSON representation   ||
   || fadetime_sec:       ||    numeric    ||        numeric          ||
   =====================================================================
"""

import lightshows.utilities
from lightshows.metashow import Lightshow, InvalidStrip, InvalidConf, InvalidParameters
import logging as log


class Clear(Lightshow):
    minimal_number_of_leds = 1

    def run(self):
        # check if we have enough LEDs
        if self.strip.numLEDs < self.minimal_number_of_leds:
            log.critical("This show needs a strip of at least {} LEDs to run correctly".format(minimal_number_of_leds))
            return

        fadetime_sec = self.parameters["fadetime_sec"]

        if fadetime_sec > 0:
            lightshows.utilities.blend_whole_strip_to_color(self.strip, (0, 0, 0), fadetime_sec)  # fadeout
        self.strip.clearStrip()

    def check_runnable(self):
        # is "fadetime_sec" set?
        if "fadetime_sec" not in self.parameters:
            raise InvalidParameters("fadetime_sec missing!")

        # it is set, so we can import it now
        fadetime_sec = self.parameters["fadetime_sec"]

        # is "fadetime_sec" numeric?
        param_type = type(fadetime_sec)
        if not (param_type is int or param_type is float):
            raise InvalidParameters("fadetime_sec is not a numeric type (instead {}!".format(param_type))

        # is "fadetime_sec" positive?
        if fadetime_sec < 0:
            raise InvalidParameters("fadetime_sec must be a _positive_ number! (instead {})!".format(fadetime_sec))

        # do we have at least one LED
        if self.strip.numLEDs < self.minimal_number_of_leds:
            raise InvalidStrip("This show needs a strip of at least {} LEDs to run!".format(self.strip.numLEDs))
