"""
Helpers for 102shows
(c) 2016 Simon Leiner
licensed under the GNU Public License, version 2

Helpful functions that are used throughout 102shows
"""

__all__ = ['color', 'exceptions', 'mqtt', 'preprocessors', 'verify']


def get_logo(filename: str ='../logo') -> str:
    with open(filename, encoding='unicode_escape') as file:
        contents = file.read()
    return contents.rstrip().rstrip()  # return without newline at the end


def get_version(filename: str ='../version') -> str:
    with open(filename) as file:
        contents = file.read()
    return contents.rstrip().rstrip()  # return without newline at the end
