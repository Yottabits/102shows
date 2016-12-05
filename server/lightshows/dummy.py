"""
dummy
(c) 2016 Simon Leiner

This show does nothing with the strip
"""

import logging as log
import time

from lightshows.templates.base import *


class Dummy(Lightshow):
    def check_runnable(self):
        return True

    def run(self):
        log.info("Dummy show started")
        time.sleep(4)
        self.stop()

    def stop(self):
        log.info("Dummy show stopped")
