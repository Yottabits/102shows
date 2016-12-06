"""
Rainbox
(c) 2015 Martin Erzberger, 2016 Simon Leiner

Rotates a rainbow color wheel around the strip.

Parameters:
    None
"""

from lightshows.templates.colorcycle import *


class Rainbow(ColorCycle):
    def init(self):
        pass

    def update(self, current_step: int, current_cycle: int):
        # One cycle = One trip through the color wheel, 0..254
        # Few cycles = quick transition, lots of cycles = slow transition
        # -> LED 0 goes from index 0 to 254 in numStepsPerCycle cycles. So it might have to step up
        #     more or less than one index depending on numStepsPerCycle.
        # -> The other LEDs go up to 254, then wrap around to zero and go up again until the last one is just
        #     below LED 0. This way, the strip always shows one full rainbow, regardless of the number of LEDs
        scale_factor = 255 / self.strip.numLEDs  # Value for the index change between two neighboring LEDs
        start_index = 255 / self.numStepsPerCycle * current_step  # Value of LED 0
        for i in range(self.strip.numLEDs):
            led_index = start_index + i * scale_factor  # Index of LED i, not rounded and not wrapped at 255
            led_index_rounded_and_wrapped_around = int(round(led_index, 0)) % 255  # Now rounded and wrapped
            pixel_color = self.strip.wheel(led_index_rounded_and_wrapped_around)  # Get the actual color out of wheel
            self.strip.setPixelRGB(i, pixel_color);
        return 1  # All pixels are set in the buffer, so repaint the strip now
