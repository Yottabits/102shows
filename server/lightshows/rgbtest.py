"""
RGBTest
(c) 2016 Simon Leiner

turns on all red, then all green, then all blue leds and then all together

Parameters:
    None
"""
import time

import lightshows.solidcolor
import lightshows.utilities
from lightshows.templates.base import *


class RGBTest(Lightshow):
    def check_runnable(self) -> bool:
        if self.parameters:
            return False  # there should not be any parameters
        else:
            return True

    def run(self):
        while True:
            # single leds
            lightshows.utilities.blend_whole_strip_to_color(self.strip, (255, 0, 0), fadetime_sec=0)
            time.sleep(10)
            lightshows.utilities.blend_whole_strip_to_color(self.strip, (0, 255, 0), fadetime_sec=0)
            time.sleep(10)
            lightshows.utilities.blend_whole_strip_to_color(self.strip, (0, 0, 255), fadetime_sec=0)
            time.sleep(10)

            # all leds together
            lightshows.utilities.blend_whole_strip_to_color(self.strip, (255, 255, 255), fadetime_sec=0)
            time.sleep(10)

            # clear strip
            self.strip.clearStrip()
            time.sleep(5)
