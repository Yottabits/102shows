from DefaultConfig import *

# load default configuration
configuration = Configuration()

# This configuration file is written in Python syntax.
# If you do not know what that means, here is the gist:
#  - Lines that begin with # are comments. Like this one
#  - You write your configuration like:
#           configuration.Group.Subgroups.setting = value
#  - To see all categories and possible settings, look at DefaultConfig.py
#  - Strings are enclosed in " ", for example:
#           configuration.sys_name = "MySuperCoolName"
#  - Each preset has a trailing # and whitespace. Remove them them
#    to activate the line. It is important that configuration.bla...
#    starts right AT THE VERY BEGINNING of the line. Or else, you will
#    encounter errors.


# Really important! Set the name of your new shiny LED system
configuration.sys_name = "MySuperCoolLEDStripYeah"  # should only contain letters (and numbers, if necessary)


# How detailed should the information on the console be? Uncomment the line that fits
# to your wishes by removing the # and the whitespace at the beginning of the line:
configuration.log_level = log.ERROR    # show only if something goes really wrong
configuration.log_level = log.WARNING  # give me some more information!
configuration.log_level = log.INFO     # I really want to know what is going on
configuration.log_level = log.DEBUG    # I am currently debugging this software

# Strip
# =====
# To set the right driver, uncomment the line that fits to your setup
# by removing the # and the whitespace at the beginning of the line:
# configuration.Strip.Driver = APA102  # APA102 (aka DotStar)
# configuration.Strip.Driver = Dummy   # no actual LED strip (useful for development)

# adjust the following lines how you want:
configuration.Strip.num_leds = 144              # number of LEDs in your strip
configuration.Strip.max_brightness = 75         # maximum brightness allowed (from 0 to 100)
configuration.Strip.initial_brightness = 50     # the brightness that is set when 102shows starts

# MQTT
# ====
# If you have mosquitto running on the same pi as the one where 102shows
# is installed, you do not need to change the lines below.
# Otherwise I assume you know what to put there ;-)

configuration.MQTT.Broker.host = "localhost"
configuration.MQTT.Broker.port = 1883
# configuration.MQTT.username = ...
# configuration.MQTT.password = ...
