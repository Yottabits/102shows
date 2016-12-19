from drivers import *

drivers = {'apa102': apa102.APA102,
           'dummy': dummy.DummyDriver
           }


def get_driver(driver_name: str):
    normalized_name = driver_name.lower()
    return drivers[normalized_name]
