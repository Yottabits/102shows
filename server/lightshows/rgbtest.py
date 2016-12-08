"""
RGBTest
(c) 2016 Simon Leiner

turns on all red, then all green, then all blue leds and then all together

Parameters:
    No parameters
"""
import time

from lightshows.templates.base import *
from lightshows.utilities.general import blend_whole_strip_to_color
from lightshows.utilities.verifyparameters import InvalidParameters


class RGBTest(Lightshow):
    def set_parameter(self, param_name: str, value):
        raise InvalidParameters.unknown(param_name)

    def check_runnable(self):
        return True

    def run(self):
        while True:
            # single leds
            blend_whole_strip_to_color(self.strip, (255, 0, 0), fadetime_sec=0)
            time.sleep(10)
            blend_whole_strip_to_color(self.strip, (0, 255, 0), fadetime_sec=0)
            time.sleep(10)
            blend_whole_strip_to_color(self.strip, (0, 0, 255), fadetime_sec=0)
            time.sleep(10)

            # all leds together
            blend_whole_strip_to_color(self.strip, (255, 255, 255), fadetime_sec=0)
            time.sleep(10)

            # clear strip
            self.strip.clear_strip()
            time.sleep(5)
