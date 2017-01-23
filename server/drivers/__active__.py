# 102shows list of active drivers
# (c) 2016-2017 Simon Leiner
# licensed under the GNU Public License, version 2


from drivers import *

drivers = {'apa102': apa102.APA102,
           'dummy': dummy.DummyDriver
           }
"""\
This maps the driver names for configuration to the according
driver class.
"""


def get_driver(driver_name: str):
    """
    Gets the driver class for a specified strip name

    :param driver_name: The name of the strip (or strip driver)
        as in :py:attribute:`drivers`

    :return: The class of the wanted driver

    :raises :py:exception:`KeyError` if the specified driver name
        is not found
    """
    normalized_name = driver_name.lower()
    return drivers[normalized_name]
