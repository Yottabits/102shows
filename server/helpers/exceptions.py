"""
Exceptions for 102shows
(c) 2016 Simon Leiner
licensed under the GNU Public License, version 2

The module defines some own exception classes:
 - InvalidParameters (as used by the functions above)
 - InvalidConf
 - InvalidStrip
"""


class InvalidStrip(Exception):
    """
    use if something is wrong with the strip
    for example: not enough LEDs to run the selected lightshow
    """
    pass


class InvalidConf(Exception):
    """
    use if something in the configuration will not work
    for what the user has chosen
    """
    pass


class InvalidParameters(Exception):
    """
    use when given parameters are not valid
    """
    @staticmethod
    def unknown(param_name: str = None):
        if param_name:
            debug_str = "Parameter \"{name}\" is unknown!".format(name=param_name)
        else:
            debug_str = "Parameter is unknown!"
        return InvalidParameters(debug_str)

    @staticmethod
    def missing(param_name: str = None):
        if param_name:
            debug_str = "Parameter \"{name}\" is missing!".format(name=param_name)
        else:
            debug_str = "Parameter is missing!"
        return InvalidParameters(debug_str)
