"""
RGBTest
(c) 2016 Simon Leiner
licensed under the GNU Public License, version 2
"""

from helpers.color import blend_whole_strip_to_color
from lightshows.templates.base import *


class RGBTest(Lightshow):
    """
    turns on all red, then all green, then all blue leds and then all together

    No parameters necessary
    """
    def init_parameters(self):
        pass

    def check_runnable(self):
        return True

    def run(self):
        while True:
            # single leds
            blend_whole_strip_to_color(self.strip, (255, 0, 0), fadetime_sec=0)
            self.sleep(10)
            blend_whole_strip_to_color(self.strip, (0, 255, 0), fadetime_sec=0)
            self.sleep(10)
            blend_whole_strip_to_color(self.strip, (0, 0, 255), fadetime_sec=0)
            self.sleep(10)

            # all leds together
            blend_whole_strip_to_color(self.strip, (255, 255, 255), fadetime_sec=0)
            self.sleep(10)

            # clear strip
            self.strip.clear_strip()
            self.sleep(5)
