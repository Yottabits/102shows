from drivers.fake_apa102 import APA102
from lightshows.solidcolor import SolidColor
import time


class RGBTest:
    def __init__(self, strip: APA102):
        self.strip = strip
        self.show_color = SolidColor(strip)

    def run(self, dim: float = 1.0):
        brightness = int(dim * 255)
        while True:
            # single leds
            self.show_color.run(brightness, 0, 0)
            time.sleep(10)
            self.show_color.run(0, brightness, 0)
            time.sleep(10)
            self.show_color.run(0, 0, brightness)
            time.sleep(10)

            # all leds together
            self.show_color.run(brightness, brightness, brightness)
            time.sleep(10)

            # clear strip
            self.strip.clearStrip()
            time.sleep(5)

