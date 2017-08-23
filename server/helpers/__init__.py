# Helpers for 102shows
# (c) 2016-2017 Simon Leiner
# licensed under the GNU Public License, version 2

"""\
This module includes several helpful functions for 102shows to use.
Any functionality that could be used in multiple parts of the program should be defined here.

For example:
    - checking if color tuples are valid: :py:func:`helpers.verify.rgb_color_tuple`
    - add two color tuples: :py:func:`helpers.color.add_tuples`
    - interpreting an incoming MQTT message: :py:mod:`helpers.mqtt`
    - parsing the :file:`config.yml` file: :py:mod:`helpers.configparser`

The module also includes some functions that are just too generic to include them in the one
place where they are used.

For example:
    - getting the 102shows version: :py:func:`helpers.get_logo`
    - getting the colored 102shows logo: :py:func:`helpers.get_version`
"""

__all__ = ['color', 'exceptions', 'mqtt', 'preprocessors', 'verify']


def get_logo(filename: str ='../logo') -> str:
    """\
    Returns the colored 102shows logo. It is read from :file:`/path/to/102shows/logo`

    :param filename: You can specify another logo source file, if you want.

    :return: The logo as a multiline string. The colors are included as escape characters.
    """
    with open(filename, encoding='unicode_escape') as file:
        contents = file.read()
    return contents.rstrip().rstrip()  # return without newline at the end


def get_version(filename: str ='../version') -> str:
    """\
    Returns the current 102shows version as a string that is read from a special version file

    :param filename: Name of the version file. If no name is supplied, the standard file
        ``/path/to/102shows/version`` will be used

    :return: version string (as in the file))
    """
    with open(filename) as file:
        contents = file.read()
    return contents.rstrip().rstrip()  # return without newline at the end
