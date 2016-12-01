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
# configuration.mqtt.username = ...
# configuration.mqtt.password = ...


# A list of available shows
configuration.shows = {
    'clear': clear,
    'dummy': dummy,
    'rainbow': rainbow,
    'rgbtest': rgbtest,
    'spinthebottle': spinthebottle,
    'solidcolor': solidcolor,
    'strandtest': strandtest,
    'theaterchase': theaterchase,
    'twocolorblend': twocolorblend,
}
