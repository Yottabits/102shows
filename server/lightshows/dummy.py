"""
dummy
(c) 2016 Simon Leiner

This show does nothing with the strip
"""

import logging
from drivers.fake_apa102 import APA102
from DefaultConfig import Configuration


# end immediately after start
def run(strip: APA102, conf: Configuration, parameters: dict):
    logging.info("Dummy show started")
    stop()


# what could go wrong?
def parameters_valid(parameters: dict) -> bool:
    return True


def stop():
    logging.info("Dummy show stopped")
