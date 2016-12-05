"""
Rainbox
(c) 2015 Martin Erzberger, 2016 Simon Leiner

Rotates a rainbow color wheel around the strip.

Parameters:
    None
"""

from lightshows.templates.colorcycle import *


class Rainbow(ColorCycle):
    def init(self, strip):
        pass

    def update(self, strip: LEDStrip, numStepsPerCycle, currentStep, currentCycle):
        # One cycle = One thrip through the color wheel, 0..254
        # Few cycles = quick transition, lots of cycles = slow transition
        # -> LED 0 goes from index 0 to 254 in numStepsPerCycle cycles. So it might have to step up
        #     more or less than one index depending on numStepsPerCycle.
        # -> The other LEDs go up to 254, then wrap arount to zero and go up again until the last one is just
        #     below LED 0. This way, the strip always shows one full rainbow, regardless of the number of LEDs
        scaleFactor = 255 / strip.numLEDs  # Value for the index change between two neighboring LEDs
        startIndex = 255 / numStepsPerCycle * currentStep  # Value of LED 0
        for i in range(strip.numLEDs):
            ledIndex = startIndex + i * scaleFactor  # Index of LED i, not rounded and not wrapped at 255
            ledIndexRoundedAndWrappedAround = int(round(ledIndex, 0)) % 255  # Now rounded and wrapped
            pixelColor = strip.wheel(ledIndexRoundedAndWrappedAround)  # Get the actual color out of the wheel
            strip.setPixelRGB(i, pixelColor);
        return 1  # All pixels are set in the buffer, so repaint the strip now
