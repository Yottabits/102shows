"""
RGBTest
(c) 2016 Simon Leiner

turns on all red, then all green, then all blue leds and then all together

Parameters:
    None
"""

from drivers.apa102 import APA102
import lightshows.solidcolor
from DefaultConfig import Configuration
import time
import logging as log


minimal_number_of_leds = 1


def run(strip: APA102, conf: Configuration, parameters: dict):
    # check if we have enough LEDs
    global minimal_number_of_leds
    if strip.numLEDs < minimal_number_of_leds:
        log.critical("This show needs a strip of at least {} LEDs to run correctly".format(minimal_number_of_leds))
        return

    while True:
        # single leds
        lightshows.solidcolor.blend_to_color(strip, (255, 0, 0), fadetime_sec=0)
        time.sleep(10)
        lightshows.solidcolor.blend_to_color(strip, (0, 255, 0), fadetime_sec=0)
        time.sleep(10)
        lightshows.solidcolor.blend_to_color(strip, (0, 0, 255), fadetime_sec=0)
        time.sleep(10)

        # all leds together
        lightshows.solidcolor.blend_to_color(strip, (255, 255, 255), fadetime_sec=0)
        time.sleep(10)

        # clear strip
        strip.clearStrip()
        time.sleep(5)


def parameters_valid(parameters: dict) -> bool:
    if parameters:
        return False  # there should not be any parameters
    else:
        return True
