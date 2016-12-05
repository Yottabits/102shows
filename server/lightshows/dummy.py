"""
dummy
(c) 2016 Simon Leiner

This show does nothing with the strip
"""

import logging as log
from drivers.apa102 import APA102 as LEDStrip
from DefaultConfig import Configuration
from lightshows.metashow import Lightshow
import time


class Dummy(Lightshow):
    def check_runnable(self):
        return True

    def run(self):
        log.info("Dummy show started")
        time.sleep(4)
        self.stop()

    def stop(self):
        log.info("Dummy show stopped")
