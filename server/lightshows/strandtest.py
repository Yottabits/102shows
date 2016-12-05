"""
Strand Test
(c) 2015 Martin Erzberger, 2016 Simon Leiner

Displays a classical LED test

Parameters:
    None
"""

from lightshows.colorcycletemplate import ColorCycleTemplate
from drivers.apa102 import APA102


class StrandTest(ColorCycleTemplate):
    def init(self, strip: APA102):
        self.color = 0x000000  # Initialize with black

    def update(self, strip: APA102, numStepsPerCycle, currentStep, currentCycle):
        # One cycle = The 9 Test-LEDs wander through numStepsPerCycle LEDs.
        if currentStep == 0:
            self.color >>= 8  # Red->green->blue->black
        if self.color == 0:
            self.color = 0xFF0000  # If black, reset to red

        head = (currentStep + 9) % numStepsPerCycle  # The head pixel that will be turned on in this cycle
        tail = currentStep  # The tail pixel that will be turned off
        strip.setPixelRGB(head, self.color)  # Paint head
        strip.setPixelRGB(tail, 0)  # Clear tail

        return 1  # Repaint is necessary
