import apa102

class TwoColorBlend:

    def __init__(self, strip: apa102.APA102):
        self.strip = strip

    def dim(self, color: tuple, dim: float):
        r, g, b = color
        r = int(dim * r)
        g = int(dim * g)
        b = int(dim * b)
        new_color = (r, g, b)
        return new_color

    def merge(self, tuple1: tuple, tuple2: tuple):
        r1, g1, b1 = tuple1
        r2, g2, b2 = tuple2
        merged_tuple = (r1 + r2, g1 + g2, b1 + b2)
        return merged_tuple

    def run(self, color1: tuple, color2: tuple):
        for led in range(self.strip.numLEDs):
            normal_distance = led / self.strip.numLEDs
            component1 = self.dim(color1, 1 - normal_distance)
            component2 = self.dim(color2, normal_distance)
            led_color = self.merge(component1, component2)
            self.strip.setPixel(led, *led_color)
        self.strip.show()
