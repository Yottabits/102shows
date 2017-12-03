# Rainbow
# (c) 2015 Martin Erzberger, 2016-2017 Simon Leiner
# licensed under the GNU Public License, version 2
import random

from helpers.color import wheel
from lightshows.templates.colorcycle import *


class Starlight(ColorCycle):
    """\
    Rotates a rainbow color wheel around the strip.

    No parameters necessary
    """

    def __init__(self, strip: LEDStrip, parameters: dict):
        super().__init__(strip, parameters)
        self.state = {}
        self.length = 10
        self.color = (255, 180, 50)

    def init_parameters(self):
        super().init_parameters()
        self.set_parameter('num_steps_per_cycle', 255)
        self.set_parameter('pause_sec', 0.02)

    def before_start(self):
        pass

    def update(self, current_step: int, current_cycle: int) -> bool:
        t = current_step + current_cycle * 256

        if random.randint(0, 100) > 90:
            self.state[random.randint(0, self.strip.num_leds - 1)] = t + self.length

        self.strip.clear_buffer()

        for pos, end in self.state.items():
            brightness = 1.0 / self.length * (end - t)
            self.strip.set_pixel(pos, *self.color)
            self.strip.set_brightness(pos, brightness)

        self.state = { pos: end for pos, end in self.state.items() if end > t }

        return True  # All pixels are set in the buffer, so repaint the strip now
