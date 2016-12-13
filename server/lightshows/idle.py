"""
Idle Show
(c) 2016 Simon Leiner
"""
from time import sleep

from lightshows.templates.base import *
from lightshows.utilities import verifyparameters as verify


class Idle(Lightshow):
    def run(self):
        while True:
            log.debug("refreshing strip")
            self.strip.show()
            sleep(self.pause_sec)

    def init_parameters(self):
        self.pause_sec = 0.1

    def set_parameter(self, param_name: str, value):
        if param_name == "pause_sec":
            verify.not_negative_numeric(value, "pause_sec")


    def check_runnable(self):
        pass  # always runnable
