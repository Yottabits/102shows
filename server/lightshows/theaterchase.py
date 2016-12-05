"""
Theater Chase
(c) 2015 Martin Erzberger, 2016 Simon Leiner

Theater Chase: https://www.youtube.com/watch?v=rzDw4Yu_S6U

Parameters:
    None
"""

import logging as log

from lightshows.templates.colorcycletemplate import *


class TheaterChase(ColorCycleTemplate):
    def init(self, strip):
        pass

    def update(self, strip: LEDStrip, numStepsPerCycle, currentStep, currentCycle):
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