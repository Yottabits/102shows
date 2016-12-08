from DefaultConfig import *
from lightshows import *

# load default configuration
configuration = Configuration()

################################# CUSTOM SETTINGS #################################
# set your own parameters here, look at DefaultConfig.py for all possible options #
###################################################################################
# for example:
# configuration.sys_name = "MyLED"

# configuration.Strip.num_leds = 144
# configuration.Strip.max_brightness = 20
# configuration.Strip.initial_brightness = 14
# configuration.Strip.Driver = APA102

# configuration.MQTT.Broker.host = "127.0.0.1"
# configuration.MQTT.Broker.port = 1883
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
