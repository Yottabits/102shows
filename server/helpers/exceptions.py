# Exceptions for 102shows
# (c) 2016-2017 Simon Leiner
# licensed under the GNU Public License, version 2

"""This module defines some exception classes specific to 102shows:"""


class DescriptiveException(Exception):
    """\
    This type of exception must contain a value (usually a string)
    that is used as the string representation of the exception
    """

    def __init__(self, value):
        self.value = value
        pass

    def __str__(self) -> str:
        return repr(self.value)


class InvalidStrip(DescriptiveException):
    """\
    Use if something is wrong with the strip.

    **For example:** not enough LEDs to run the selected lightshow
    """

    pass


class InvalidConf(DescriptiveException):
    """\
    Use if something in the configuration will not work
    for what the user has chosen in the config file.
    """

    pass


class InvalidParameters(DescriptiveException):
    """\
    Use when given parameters (for a lightshow) are not valid
    """

    @staticmethod
    def unknown(param_name: str = None):
        """\
        .. todo:: document!
        """
        if param_name:
            debug_str = "Parameter \"{name}\" is unknown!".format(name=param_name)
        else:
            debug_str = "Parameter is unknown!"
        return InvalidParameters(debug_str)

    @staticmethod
    def missing(param_name: str = None):
        """\
        .. todo:: document!
        """
        if param_name:
            debug_str = "Parameter \"{name}\" is missing!".format(name=param_name)
        else:
            debug_str = "Parameter is missing!"
        return InvalidParameters(debug_str)
