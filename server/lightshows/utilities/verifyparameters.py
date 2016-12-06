def numeric(testing, param_name: str = None, minimum: float = None, maximum: float = None):
    if param_name:
        debug_str = "Parameter \"{name}\" must be a number".format(name=param_name)
    else:
        debug_str = "Parameter must be a number"

    if minimum is not None and maximum is not None:
        debug_str += " between {min} and {max}".format(min=minimum, max=maximum)
    elif minimum is not None:
        debug_str += " >= {}".format(minimum)
    elif maximum is not None:
        debug_str += " <= {}".format(maximum)

    debug_str += "! (got: {})".format(testing)

    if type(testing) not in (float, int):
        raise InvalidParameters(debug_str)
    if minimum is not None and testing < minimum:
        raise InvalidParameters(debug_str)
    if maximum is not None and testing > maximum:
        raise InvalidParameters(debug_str)


def not_negative_numeric(testing, param_name: str = None):
    if type(testing) not in (float, int) or testing < 0:
        if param_name:
            debug_str = "Parameter \"{name}\" must be a non-negative number!".format(name=param_name)
        else:
            debug_str = "Parameter must be a not-negative number!"
        raise InvalidParameters(debug_str)


def positive_numeric(testing, param_name: str = None):
    if type(testing) not in (float, int) or testing <= 0:
        if param_name:
            debug_str = "Parameter \"{name}\" must be a positive number!".format(name=param_name)
        else:
            debug_str = "Parameter must be a positive number!"
        raise InvalidParameters(debug_str)


def integer(testing, param_name: str = None, minimum: float = None, maximum: float = None):
    if param_name:
        debug_str = "Parameter \"{name}\" must be an integer".format(name=param_name)
    else:
        debug_str = "Parameter must be an integer"

    if minimum is not None and maximum is not None:
        debug_str += " between {min} and {max}".format(min=minimum, max=maximum)
    elif minimum is not None:
        debug_str += " >= {}".format(minimum)
    elif maximum is not None:
        debug_str += " <= {}".format(maximum)

    debug_str += "! (got: {})".format(testing)

    if type(testing) is not int:
        raise InvalidParameters(debug_str)
    if minimum is not None and testing < minimum:
        raise InvalidParameters(debug_str)
    if maximum is not None and testing > maximum:
        raise InvalidParameters(debug_str)


def not_negative_integer(testing, param_name: str = None):
    if type(testing) is not int or testing < 0:
        if param_name:
            debug_str = "Parameter \"{name}\" must be a non-negative integer!".format(name=param_name)
        else:
            debug_str = "Parameter must be a not-negative integer!"
        raise InvalidParameters(debug_str)


def positive_integer(testing, param_name: str = None):
    if type(testing) is not int or testing <= 0:
        if param_name:
            debug_str = "Parameter \"{name}\" must be a positive integer!".format(name=param_name)
        else:
            debug_str = "Parameter must be a positive integer!"
        raise InvalidParameters(debug_str)


def boolean(testing, param_name: str = None):
    if type(testing) is not bool:
        if param_name:
            debug_str = "Parameter \"{name}\" must be a boolean value!".format(name=param_name)
        else:
            debug_str = "Parameter must be a boolean value!"
        raise InvalidParameters(debug_str)


def rgb_color_tuple(testing, param_name: str = None):
    if param_name:
        debug_str = "Parameter \"{name}\" must be an RGB color tuple!".format(name=param_name)
    else:
        debug_str = "Parameter must be an RGB color tuple!"

    if type(testing) is not tuple:
        raise InvalidParameters(debug_str)

    if len(testing) is not 3:  # an rgb tuple has three components
        raise InvalidParameters(debug_str)

    for component in testing:
        if type(component) is not int:
            raise InvalidParameters(debug_str)
        if not (0 <= component <= 255):
            raise InvalidParameters(debug_str)


class InvalidStrip(Exception):
    pass


class InvalidConf(Exception):
    pass


class InvalidParameters(Exception):
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