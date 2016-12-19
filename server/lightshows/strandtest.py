"""
Strand Test
(c) 2015 Martin Erzberger, 2016 Simon Leiner
licensed under the GNU Public License, version 2
"""

from lightshows.templates.colorcycle import *


class StrandTest(ColorCycle):
    """
    Displays a classical LED test

    No parameters necessary
    """
    def init_parameters(self):
        super().init_parameters()
        self.set_parameter('num_steps_per_cycle', self.strip.num_leds)

    def before_start(self):
        self.color = 0x000000  # Initialize with black

    def update(self, current_step: int, current_cycle: int):
        # One cycle = The 9 Test-LEDs wander through numStepsPerCycle LEDs.
        if current_step == 0:
            self.color >>= 8  # Red->green->blue->black
        if self.color == 0:
            self.color = 0xFF0000  # If black, reset to red

        head = (current_step + 9) % self.p['num_steps_per_cycle']  # The head pixel that will be turned on in this cycle
        tail = current_step  # The tail pixel that will be turned off
        self.strip.set_pixel_bytes(head, self.color)  # Paint head
        self.strip.set_pixel_bytes(tail, 0)  # Clear tail

        return True  # Repaint is necessary
