"""
Preprocessors for 102shows parameters
(c) 2016 Simon Leiner
licensed under the GNU Public License, version 2
"""


def list_to_tuple(value):
    if type(value) is list:
        value = tuple(value)
    return value
