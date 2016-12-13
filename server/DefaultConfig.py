# THIS IS THE DEFAULT CONFIGURATION FILE, DO NOT CHANGE THIS!
# COPY config.example.py TO config.py AND ADJUST THE CONFIGURATION THERE!

import logging as log
from drivers.apa102 import APA102
from drivers.dummy import DummyDriver as Dummy
from lightshows import *


class Configuration:
    sys_name = None  # string
    log_level = log.INFO  # standard log level

    shows = {'clear': clear.Clear,  # A list of available shows
             'rainbow': rainbow.Rainbow,
             'rgbtest': rgbtest.RGBTest,
             'spinthebottle': spinthebottle.SpinTheBottle,
             'solidcolor': solidcolor.SolidColor,
             'theaterchase': theaterchase.TheaterChase,
             'twocolorblend': twocolorblend.TwoColorBlend,
             }

    class MQTT:
        prefix = "led"
        general_path = "{prefix}/{sys_name}/show/{show_name}/{command}"
        notification_path = "{prefix}/{sys_name}/notification"
        username = None
        password = None

        class Broker:
            host = "localhost"
            port = 1883
            keepalive = 60  # in seconds

    class Strip:
        Driver = APA102
        num_leds = None  # integer
        max_clock_speed_hz = 4000000  # 4 MHz is the maximum for "large" strips of more than 500 LEDs.
        initial_brightness = 50  # integer from 0 to 100
        max_brightness = 75  # maximum brightness
