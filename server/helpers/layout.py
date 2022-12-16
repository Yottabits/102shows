import logging

from drivers import LEDStrip

log = logging.getLogger(__name__)

class Layout:

    def __init__(self, strip: LEDStrip, dead=102, mirror=True):
        self.strip = strip
        self.length = strip.num_leds
        self.dead = dead
        self.mirror = mirror

    @property
    def block(self):
        return int((self.length - self.dead) / (2 if self.mirror else 1))

    def set_pixel(self, led_num: int, red: float, green: float, blue: float) -> None:
        self.set_pixel_func(self.strip.set_pixel, led_num, red, green, blue)

    def set_pixel_func(self, func, led_num: int, red: float, green: float, blue: float) -> None:
        func(led_num, red, green, blue)
        if self.mirror:
            func(self.length -1 - led_num, red, green, blue)
