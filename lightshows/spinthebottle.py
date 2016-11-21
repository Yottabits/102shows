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

    def highlight(self, position: int, highlight_radius: int = 3):
        for led in range(0, self.strip.numLEDs):
            distance = abs(led - position)  # distance to highlight center
            if distance <= highlight_radius:
                dim_factor = (1 - (distance / highlight_radius)) ** 2
                color = util.dim(self.highlight_color, dim_factor)
                self.strip.setPixel(led, *color)
            else:
                self.strip.setPixel(led, *self.background_color)
        self.strip.show()

    def run(self, time_sec: float = 5, fadeout: bool = False):
        section_width = (self.upper_border - self.lower_border) // self.highlight_sections
        target_led = random.randrange(self.lower_border, self.upper_border, section_width)
        frame_time = time_sec / (3 * self.highlight_sections)  # 3 for the three roundtrips

        # go round the strip one time
        for led in range(self.lower_border, self.upper_border + 1, section_width):
            self.highlight(led, highlight_radius=section_width // 2)
            time.sleep(frame_time)
        for led in range(self.upper_border + 1, self.lower_border, -section_width):
            self.highlight(led, highlight_radius=section_width // 2)
            time.sleep(frame_time)

        # focus on target
        for led in range(self.lower_border, target_led, section_width):
            self.highlight(led)
            relative_distance = abs(led - target_led) / self.strip.numLEDs
            time.sleep(0.0006 * time_sec / relative_distance)  # slow down a little
        self.highlight(target_led, highlight_radius=section_width // 2)

        if fadeout:
            time.sleep(10)
            util.linear_fadeout(self.strip, fadetime_sec=2)

    def set_borders(self, lower: int, upper: int):
        self.lower_border = lower
        self.upper_border = upper
