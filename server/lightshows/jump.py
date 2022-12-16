#!/usr/bin/env python3

import logging
import math

from drivers import LEDStrip
from helpers.layout import Layout
from lightshows.templates.colorcycle import ColorCycle

log = logging.getLogger(__name__)


class Ball(object):

    def __init__(self, height, stripe, color):
        self.height = height - stripe
        self.stripe = stripe
        self.width = 2 * math.sqrt(self.height)
        self.center = self.width / 2.0
        self.color = color
        self.period = 0
        self.next = False

    def get_pos(self, t):
        current_period = int(math.floor(t / self.width))

        if self.period != current_period:
            self.period = current_period
            self.next = True

        return int(self.height - (t % self.width - self.center) ** 2)

    def is_next(self):
        if self.next:
            log.debug("next %d", self.height)
            self.next = False
            return True
        return False


class Jump(ColorCycle):
    """\
    Rotates a rainbow color wheel around the strip.

    No parameters necessary
    """

    def __init__(self, strip: LEDStrip, parameters: dict):
        super().__init__(strip, parameters)
        self.state = {}
        self.stripe = 1
        self.balls = ()
        self.spare_colors = [(0, 255, 255)]

    def init_parameters(self):
        super().init_parameters()
        self.set_parameter('num_steps_per_cycle', 255)
        self.set_parameter('pause_sec', 0.005)

    def before_start(self):
        self.balls = (
            Ball(self.layout.block, self.stripe, (255, 0, 0)),
            Ball(self.layout.block * 0.5, self.stripe, (0, 255, 0)),
            Ball(self.layout.block * 0.75, self.stripe, (255, 255, 0)),
            Ball(self.layout.block * 0.88, self.stripe, (255, 0, 255)),
            Ball(self.layout.block * 0.66, self.stripe, (0, 0, 255))
        )

    def update(self, current_step: int, current_cycle: int) -> bool:
        t = (current_step + current_cycle * 256) * 0.1

        self.strip.clear_buffer()

        for offset in range(0, self.stripe):
            for ball in self.balls:
                pos = ball.get_pos(t)
                index = pos + offset
                self.layout.set_pixel(index, *ball.color)

                if ball.is_next():
                    self.spare_colors.insert(0, ball.color)
                    ball.color = self.spare_colors.pop()

        return True
