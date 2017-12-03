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
    def init_parameters(self):
        super().init_parameters()
        self.state = {}
        self.length = 5
        self.color = (255, 180, 50)

    def before_start(self):
        pass

    def update(self, current_step: int, current_cycle: int) -> bool:
        t = current_cycle

        if random.randint(0, 100) > 95:
            self.state[random.randint(0, self.strip.num_leds)] = t + LENGTH

        for pos in range(self.strip.num_leds):
            self.strip.set_pixel(pos, 0, 0, 0)

        for pos, end in self.state.items():
            brightness = 100 / self.length * (end - t)
            self.strip.set_pixel(pos, *self.color, brightness=brightness)

        self.state = { pos: end for pos, end in self.state.items() if end > t }

        return True  # All pixels are set in the buffer, so repaint the strip now
