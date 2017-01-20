# Exceptions for 102shows
# (c) 2016-2017 Simon Leiner
# licensed under the GNU Public License, version 2

"""\
The module defines some own exception classes:
 - InvalidParameters (as used by the functions above)
 - InvalidConf
 - InvalidStrip
"""


class InvalidStrip(Exception):
    """\
    Use if something is wrong with the strip.

    **For example:** not enough LEDs to run the selected lightshow
    """
    pass


class InvalidConf(Exception):
    """\
    Use if something in the configuration will not work
    for what the user has chosen in the config file.
    """
    pass


class InvalidParameters(Exception):
    """\
    Use when given parameters (for a lightshow) are not valid
    """

    @staticmethod
    def unknown(param_name: str = None):  # fixme: docstring!
        if param_name:
            debug_str = "Parameter \"{name}\" is unknown!".format(name=param_name)
        else:
            debug_str = "Parameter is unknown!"
        return InvalidParameters(debug_str)

    @staticmethod
    def missing(param_name: str = None):  # fixme: docstring!
        if param_name:
            debug_str = "Parameter \"{name}\" is missing!".format(name=param_name)
        else:
            debug_str = "Parameter is missing!"
        return InvalidParameters(debug_str)
