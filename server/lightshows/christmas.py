"""
Christmas Show
(c) 2016 Simon Leiner, Jenny Schinkel
licensed under the GNU Public License, version 2

at this point more or less a quick hack
"""

from lightshows.templates.base import *
from helpers.color import SmoothBlend, blend_whole_strip_to_color
from helpers import verify
from helpers.exceptions import InvalidParameters


class Christmas(Lightshow):
    def init_parameters(self):
        self.velocity = 5
        self.num_cycles = {"merry_go_round": 3,
                           "chunk_blendover": 5,
                           "whole_blendover": 5}

    def set_parameter(self, param_name: str, value):
        if param_name == "merry_go_round":
            verify.not_negative_integer(value, "merry_go_round")
            self.num_cycles["merry_go_round"] = value
        elif param_name == "chunk_blendover":
            verify.not_negative_integer(value, "chunk_blendover")
            self.num_cycles["chunk_blendover"] = value
        elif param_name == "whole_blendover":
            verify.not_negative_integer(value, "whole_blendover")
        elif param_name == "velocity":
            verify.integer(value, "velocity", minimum=1, maximum=10)
            self.velocity = value
        else:
            raise InvalidParameters.unknown(param_name)

    def check_runnable(self):
        pass

    def run(self):
        self.mqtt.parse_parameter_changes = True

        while True:
            self.merry_go_round(self.num_cycles["merry_go_round"])
            self.chunk_blendover(self.num_cycles["chunk_blendover"])
            self.whole_blendover(self.num_cycles["whole_blendover"])

    def chunk_blendover(self, num_cycles: int = 1):
        transition = SmoothBlend(self.strip)

        chunk_size = 60
        red = 255, 0, 0
        green = 0, 255, 0
        blendtime_sec = lambda: self.velocity
        pause_sec = lambda: 3 * self.velocity

        for _ in range(num_cycles):
            for led_num in range(self.strip.num_leds):
                if led_num % (2 * chunk_size) < 1.5 * chunk_size:
                    transition.set_pixel(led_num, *red)
                else:
                    transition.set_pixel(led_num, *green)
            transition.blend(blendtime_sec())
            self.sleep(pause_sec())

            for led_num in range(self.strip.num_leds):
                if led_num % (2 * chunk_size) < 0.5 * chunk_size:
                    transition.set_pixel(led_num, *green)
                else:
                    transition.set_pixel(led_num, *red)
            transition.blend(blendtime_sec())
            self.sleep(pause_sec())

    def whole_blendover(self, num_cycles: int = 1):
        blendtime_sec = lambda: self.velocity
        pause_sec = lambda: 3 * self.velocity

        for _ in range(num_cycles):
            blend_whole_strip_to_color(self.strip, (255, 20, 10), fadetime_sec=blendtime_sec())
            self.sleep(pause_sec())
            blend_whole_strip_to_color(self.strip, (30, 255, 0), fadetime_sec=blendtime_sec())
            self.sleep(pause_sec())

    def static_red_green(self):
        red_green_segment = [(255, 20, 10), (255, 20, 10), (255, 20, 10), (255, 20, 10), (255, 20, 10), (255, 20, 10),
                             (255, 20, 10), (255, 20, 10), (255, 20, 10), (255, 20, 10), (255, 20, 10), (255, 20, 10),
                             (255, 20, 10), (255, 20, 10), (255, 20, 10), (255, 20, 10), (255, 20, 10), (255, 20, 10),
                             (255, 20, 10), (255, 20, 10), (255, 20, 10), (255, 20, 10), (255, 20, 10), (255, 20, 10),
                             (255, 20, 10), (255, 20, 10), (255, 20, 10), (255, 20, 10), (255, 20, 10), (229, 45, 8),
                             (204, 71, 7), (180, 98, 6), (154, 124, 5), (129, 149, 4), (105, 176, 3), (79, 202, 2),
                             (54, 228, 1), (30, 255, 0), (30, 255, 0), (30, 255, 0), (30, 255, 0), (30, 255, 0),
                             (30, 255, 0), (30, 255, 0), (30, 255, 0), (30, 255, 0), (30, 255, 0), (30, 255, 0),
                             (30, 255, 0), (30, 255, 0), (30, 255, 0), (30, 255, 0), (30, 255, 0), (30, 255, 0),
                             (30, 255, 0), (30, 255, 0), (30, 255, 0), (30, 255, 0), (54, 228, 1), (79, 202, 2),
                             (105, 176, 3), (129, 149, 4), (154, 124, 5), (180, 98, 6), (204, 71, 7), (229, 45, 8)]
        transition = SmoothBlend(self.strip)
        for led_num in range(self.strip.num_leds):
            transition.set_pixel(led_num, *(red_green_segment[led_num % len(red_green_segment)]))
        transition.blend()

    def merry_go_round(self, num_cycles: int = 1):
        pause_sec = lambda: 0.5 / self.velocity

        self.static_red_green()
        self.strip.show()
        for _ in range(num_cycles * self.strip.num_leds):
            self.strip.rotate(1)
            self.strip.show()
            self.strip.show()
            self.sleep(pause_sec())
