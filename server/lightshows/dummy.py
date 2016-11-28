"""
dummy
(c) 2016 Simon Leiner

This show does nothing with the strip
"""

import logging as log
from drivers.fake_apa102 import APA102
from DefaultConfig import Configuration


minimal_number_of_leds = 1

# end immediately after start
def run(strip: APA102, conf: Configuration, parameters: dict):
    # check if we have enough LEDs
    global minimal_number_of_leds
    if strip.numLEDs < minimal_number_of_leds:
        log.critical("This show needs a strip of at least {} LEDs to run correctly".format(minimal_number_of_leds))
        return

    log.info("Dummy show started")
    stop()


# what could go wrong?
def parameters_valid(parameters: dict) -> bool:
    return True


def stop():
    log.info("Dummy show stopped")
