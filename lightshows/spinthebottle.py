import apa102
import random
import time
import lightshows.utilities as util


class SpinTheBottle:
    def __init__(self, strip: apa102.APA102):
        self.strip = strip
        self.highlight_color = (200, 100, 0)
        self.highlight_sections = 72
        self.background_color = (0, 0, 0)
        self.lower_border = 0
        self.upper_border = self.strip.numLEDs

    def highlight(self, position: int, highlight_width=3):
        for led in range(0, self.strip.numLEDs):
            distance = abs(led - position)  # distance to highlight center
            if distance <= highlight_width:
                dim_factor = (1 - (distance / highlight_width)) ** 2
                color = util.dim(self.highlight_color, dim_factor)
                self.strip.setPixel(led, *color)
            else:
                self.strip.setPixel(led, *self.background_color)
        self.strip.show()

    def run(self, fadeout=False):
        led_step = (self.upper_border - self.lower_border) // self.highlight_sections
        target_led = random.randrange(self.lower_border, self.upper_border, led_step)

        # go round the strip one time
        for led in range(self.lower_border, self.upper_border + 1, led_step):
            self.highlight(led)
            time.sleep(0)
        for led in range(self.upper_border + 1, self.lower_border, -led_step):
            self.highlight(led)

        # focus on target
        for led in range(self.lower_border, target_led, led_step):
            self.highlight(led)
            relative_distance = abs(led - target_led) / self.strip.numLEDs
            time.sleep(0.003 / relative_distance)  # slow down a little
        self.highlight(target_led)

        if(fadeout):
            time.sleep(10)
            util.linear_fadeout(self.strip, fadetime_sec=2)

    def go_round(self):
        self.strip.clearStrip()
        for led in range(self.strip.numLEDs):
            self.strip.setPixel(led, *self.highlight_color)
        self.strip.show()
        self.strip.show()
        self.strip.show()

    def set_borders(self, lower: int, upper: int):
        self.lower_border = lower
        self.upper_border = upper
