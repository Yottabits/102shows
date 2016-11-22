import time
from drivers.fake_apa102 import APA102


def dim(undimmed: tuple, factor: float) -> tuple:
    """ multiply all components of :param undimmed with :param factor
    :return: resulting vector, as int
    """
    dimmed = ()
    for i in undimmed:
        i = int(factor * i)  # brightness needs to be an integer
        dimmed = dimmed + (i,)  # merge tuples
    return dimmed


def linear_fadeout(strip: APA102, fadetime_sec: float):
    now = time.perf_counter()
    start_time = now
    stop_time = now + fadetime_sec

    initial_color = []
    for led in range(strip.numLEDs):
        initial_color.append(strip.getPixel(led))

    while now < stop_time:
        brightness = (stop_time - now) / fadetime_sec
        for led in range(strip.numLEDs):
            color = dim(initial_color[led], brightness)
            strip.setPixel(led, *color)
        strip.show()
        now = time.perf_counter()

    strip.clearStrip()


class MeasureFPS:
    """ measures the refresh rate available to the strip"""

    def __init__(self, strip: APA102):
        self.strip = strip
        self.active_color = (255, 255, 255)
        self.passed_color = (0, 100, 100)

    def run(self) -> float:
        """runs a test on the LED strip framerate
        :return: a tuple with (framerate, time_elapsed, number_of_frames)
        """
        self.strip.clearStrip()
        self.strip.clearStrip()  # just to be sure ;)

        start_time = time.perf_counter()
        for led in range(0, self.strip.numLEDs):
            self.strip.setPixel(led, *self.active_color)
            self.strip.show()
            self.strip.setPixel(led, *self.passed_color)
        stop_time = time.perf_counter()

        time_elapsed = stop_time - start_time
        number_of_frames = self.strip.numLEDs
        framerate = number_of_frames / time_elapsed

        time.sleep(1)
        self.strip.clearStrip()
        self.strip.clearStrip()

        return (framerate, time_elapsed, number_of_frames)


def is_color_tuple(to_check) -> bool:
    """ check if :param to_check is a rgb color tuple"""
    if type(to_check) is not tuple:
        return False

    if len(to_check) is not 3:
        return False

    for component in to_check:
        if type(component) is not int:
            return False
        if not (0 <= component <= 255):
            return False

    # if no break condition is met:
    return True
