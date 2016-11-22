"""
clear

This lightshow just turns the whole strip off. It accepts no parameters
"""

import DummyAPA102 as apa102


# run this "show"
def run(strip: apa102.APA102, conf, parameters: dict):
    strip.clearStrip()


# tolerate no parameters
def parameters_valid(parameters: dict) -> bool:
    if parameters:  # if there is any parameter given
        return False
    else:
        return True
