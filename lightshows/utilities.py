import time
import apa102


def dim(undimmed: tuple, factor: float) -> tuple:
    """ multiply all components of :param undimmed with :param factor
    :return: resulting vector, as int
    """
    dimmed = ()
    for i in undimmed:
        i = int(factor * i)  # brightness needs to be an integer
        dimmed = dimmed + (i,)  # merge tuples
    return dimmed


def fadeout(fadetime_sec: float):
    pass  # @todo


class MeasureFPS:
    """ measures the refresh rate available to the strip"""

    def __init__(self, strip: apa102.APA102):
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
