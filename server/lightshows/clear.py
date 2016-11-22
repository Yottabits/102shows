"""
clear

This lightshow just turns the whole strip off. It accepts no parameters
"""

from drivers.fake_apa102 import APA102
from DefaultConfig import Configuration


# run this "show"
def run(strip: APA102, conf: Configuration, parameters: dict):
    strip.clearStrip()


# tolerate no parameters
def parameters_valid(parameters: dict) -> bool:
    if parameters:  # if there is any parameter given
        return False
    else:
        return True
