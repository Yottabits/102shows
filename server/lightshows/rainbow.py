"""
Rainbow
(c) 2015 Martin Erzberger, 2016 Simon Leiner
licensed under the GNU Public License, version 2
"""

from helpers.color import wheel
from lightshows.templates.colorcycle import *


class Rainbow(ColorCycle):
    """
    Rotates a rainbow color wheel around the strip.

    No parameters necessary
    """
    def init_parameters(self):
        super().init_parameters()
        self.set_parameter('num_steps_per_cycle', 255)

    def before_start(self):
        pass

    def update(self, current_step: int, current_cycle: int) -> bool:
        # One cycle = One trip through the color wheel, 0..254
        # Few cycles = quick transition, lots of cycles = slow transition
        # -> LED 0 goes from index 0 to 254 in numStepsPerCycle cycles. So it might have to step up
        #     more or less than one index depending on numStepsPerCycle.
        # -> The other LEDs go up to 254, then wrap around to zero and go up again until the last one is just
        #     below LED 0. This way, the strip always shows one full rainbow, regardless of the number of LEDs
        scale_factor = 255 / self.strip.num_leds  # Value for the index change between two neighboring LEDs
        start_index = 255 / self.p['num_steps_per_cycle'] * current_step  # Value of LED 0
        for i in range(self.strip.num_leds):
            led_index = start_index + i * scale_factor  # Index of LED i, not rounded and not wrapped at 255
            pixel_color = wheel(led_index % 255)  # Get the actual color out of wheel
            self.strip.set_pixel(i, *pixel_color)
        return True  # All pixels are set in the buffer, so repaint the strip now
