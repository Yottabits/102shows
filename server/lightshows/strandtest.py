"""
Strand Test
(c) 2015 Martin Erzberger, 2016 Simon Leiner

Displays a classical LED test

Parameters:
    None
"""

from lightshows.templates.colorcycle import *


class StrandTest(ColorCycle):
    def init(self):
        self.color = 0x000000  # Initialize with black

    def update(self, current_step: int, current_cycle: int):
        # One cycle = The 9 Test-LEDs wander through numStepsPerCycle LEDs.
        if current_step == 0:
            self.color >>= 8  # Red->green->blue->black
        if self.color == 0:
            self.color = 0xFF0000  # If black, reset to red

        head = (current_step + 9) % self.num_steps_per_cycle  # The head pixel that will be turned on in this cycle
        tail = current_step  # The tail pixel that will be turned off
        self.strip.setPixelRGB(head, self.color)  # Paint head
        self.strip.setPixelRGB(tail, 0)  # Clear tail

        return 1  # Repaint is necessary
