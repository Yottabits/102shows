import drivers.fake_apa102 as APA102
from DefaultConfig import Configuration


def run(strip: APA102, conf: Configuration, parameters: dict):
    red, green, blue = parameters["color"]  # get color from parameters
    SolidColor(strip).run(red, green, blue)  # set strip color


def parameters_valid(parameters: dict) -> bool:
    if "color" in parameters:
        if len(parameters["color"]) is 3:
            return True

    return False


class SolidColor:
    def __init__(self, strip: APA102):
        self.strip = strip

    def run(self, red, green, blue):
        for led in range(self.strip.numLEDs):
            self.strip.setPixel(led, red, green, blue)
        self.strip.show()
