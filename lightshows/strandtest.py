import apa102
import time


class SolidColor:
    def __init__(self, strip: apa102.APA102):
        self.strip = strip

    def run(self, red, green, blue):
        for led in range(self.strip.numLEDs):
            self.strip.setPixel(led, red, green, blue)
        self.strip.show()


class RGBTest:
    def __init__(self, strip: apa102.APA102):
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

class FPSTest:
    def __init__(self, strip: apa102.APA102):
        self.strip = strip

    def run(self):
        pass