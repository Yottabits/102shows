from DefaultConfig import *

# load default configuration
configuration = Configuration()

################################# CUSTOM SETTINGS #################################
# set your own parameters here, look at DefaultConfig.py for all possible options #
###################################################################################
# for example:
# configuration.sys_name = "MyLED"

# Strip
# =====
# - Driver
#   for APA102, write:
# configuration.Strip.Driver = APA102
#   for no driver, write:
# configuration.Strip.Driver = Dummy
# - additional settings
# configuration.Strip.num_leds = 144
# configuration.Strip.max_brightness = 75
# configuration.Strip.initial_brightness = 50

# configuration.MQTT.Broker.host = "127.0.0.1"
# configuration.MQTT.Broker.port = 1883
# configuration.MQTT.username = ...
# configuration.MQTT.password = ...
