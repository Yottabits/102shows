from lightshows.templates.base import *
from lightshows.utilities import is_rgb_color_tuple


def verify_numeric(testing, param_name: str = None):
    if type(testing) not in (float, int):
        raise InvalidParameters.not_numeric(param_name)

def verify_rgb_color_tuple(testing, param_name: str = None):
    if not is_rgb_color_tuple(testing):
        raise InvalidParameters.not_rgb_color_tuple(param_name)