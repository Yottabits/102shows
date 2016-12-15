"""
Preprocessors for 102shows parameters
(c) 2016 Simon Leiner
"""


def list_to_tuple(value):
    if type(value) is list:
        value = tuple(value)
    return value
