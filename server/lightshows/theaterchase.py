"""
Theater Chase
(c) 2015 Martin Erzberger, 2016 Simon Leiner

Theater Chase: https://www.youtube.com/watch?v=rzDw4Yu_S6U

Parameters:
    None
"""

from lightshows.colorcycletemplate import ColorCycleTemplate
from drivers.apa102 import APA102
from DefaultConfig import Configuration
import logging as log

minimal_number_of_leds = 1

def run(strip: APA102, conf: Configuration, parameters: dict):
    # check if we have enough LEDs
    global minimal_number_of_leds
    if strip.numLEDs < minimal_number_of_leds:
        log.critical("This show needs a strip of at least {} LEDs to run correctly".format(minimal_number_of_leds))
        return

    cycle = TheaterChase(strip=strip, pauseValue=0.04, numStepsPerCycle=35, numCycles=-1)
    cycle.start()  # run continuously


def parameters_valid(parameters: dict) -> bool:
    if parameters:
        return False
    else:
        return True


class TheaterChase(ColorCycleTemplate):
    def update(self, strip: APA102, numStepsPerCycle, currentStep, currentCycle):
        # One cycle = One thrip through the color wheel, 0..254
        # Few cycles = quick transition, lots of cycles = slow transition
        # Note: For a smooth transition between cycles, numStepsPerCycle must be a multiple of 7
        startIndex = currentStep % 7  # Each segment is 7 dots long: 2 blank, and 5 filled
        colorIndex = strip.wheel(int(round(255 / numStepsPerCycle * currentStep, 0)))
        for pixel in range(strip.numLEDs):
            # Two LEDs out of 7 are blank. At each step, the blank ones move one pixel ahead.
            if ((pixel + startIndex) % 7 == 0) or ((pixel + startIndex) % 7 == 1):
                strip.setPixelRGB(pixel, 0)
            else:
                strip.setPixelRGB(pixel, colorIndex)
        return 1
