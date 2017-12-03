#!/usr/bin/env python3

import apa102
import random
import time
import math

from drivers import LEDStrip
from lightshows.templates.colorcycle import ColorCycle

class Ball(object):

    def __init__(self, height, stripe):
        self.height = height - stripe
        self.stripe = stripe
        self.width = 2 * math.sqrt(self.height)
        self.center = self.width / 2.0

    def get_pos(self, t):
        return int(self.height - (t % self.width - self.center) ** 2)

class Jump(ColorCycle):
    """\
    Rotates a rainbow color wheel around the strip.

    No parameters necessary
    """

    def __init__(self, strip: LEDStrip, parameters: dict):
        super().__init__(strip, parameters)
        self.state = {}
        self.stripe = 1
        self.block = 99
        self.mirror = True
        self.balls = ()
        self.colors = ()

    def init_parameters(self):
        super().init_parameters()
        self.set_parameter('num_steps_per_cycle', 255)
        self.set_parameter('pause_sec', 0.005)

    def before_start(self):
        self.balls = (
            Ball(self.block, self.stripe),
            Ball(self.block * 0.5, self.stripe),
            Ball(self.block * 0.75, self.stripe),
            Ball(self.block * 0.88, self.stripe),
            Ball(self.block * 0.66, self.stripe)
        )
        self.colors = (
            (255, 0, 0),
            (0, 255, 0),
            (255, 255, 0),
            (255, 0, 255),
            (0, 0, 255)
        )

    pass

    def update(self, current_step: int, current_cycle: int) -> bool:
        t = (current_step + current_cycle * 256) * 0.1
        positions = (ball.get_pos(t) for ball in self.balls)

        self.strip.clear_buffer()

        for offset in range(0, self.stripe):
            for pos, color in zip(positions, self.colors):
                index = pos + offset
                self.strip.set_pixel(index, *color)
                if self.mirror:
                    self.strip.set_pixel(self.strip.num_leds - index, *color)

        return True
