"""
dummy

This show does nothing with the strip
"""

import logging


# end immediately after start
def run(strip, conf, parameters):
    logging.info("Dummy show started")
    stop()


# what could go wrong?
def parameters_valid(parameters: dict) -> bool:
    return True


def stop():
    logging.info("Dummy show stopped")
