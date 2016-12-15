"""
Idle Show
(c) 2016 Simon Leiner
"""
from time import sleep

from lightshows.templates.base import *


class Idle(Lightshow):
    """
    This lightshow refreshes the strip regularly and (inheriting from the base template)
    listens for brightness changes. It is run while no other show is running.
    """

    def init_parameters(self):
        self.register('pause_sec', 0.1, verify.not_negative_numeric)

    def check_runnable(self):
        pass  # always runnable

    def run(self):
        while True:
            self.logger.debug("refreshing strip")
            self.strip.show()
            sleep(self.p['pause_sec'])
