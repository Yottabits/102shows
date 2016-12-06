import DefaultConfig
from lightshows import *

# load default configuration
configuration = DefaultConfig.Configuration()

################################# CUSTOM SETTINGS #################################
# set your own parameters here, look at DefaultConfig.py for all possible options #
###################################################################################
# for example:
# configuration.sys_name = "MyLED"
# configuration.strip.num_leds = 144
# configuration.strip.max_brightness = 20
# configuration.strip.initial_brightness = 14
# configuration.MQTT.username = ...
# configuration.MQTT.password = ...


# A list of available shows
configuration.shows = {
    'clear': clear.Clear,
    'dummy': dummy.Dummy,
    'rainbow': rainbow.Rainbow,
    'rgbtest': rgbtest.RGBTest,
    'spinthebottle': spinthebottle.SpinTheBottle,
    'solidcolor': solidcolor.SolidColor,
    'theaterchase': theaterchase.TheaterChase,
    'twocolorblend': twocolorblend.TwoColorBlend,
}
