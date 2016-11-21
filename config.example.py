import DefaultConfig
import lightshows

# load default configuration
configuration = DefaultConfig.Configuration()


################################# CUSTOM SETTINGS #################################
# set your own parameters here, look at DefaultConfig.py for all possible options #
###################################################################################
# for example:
# configuration.sys_name = "MyLED"
# configuration.strip.num_leds = 144


# A list of available shows
shows = {
    'clear': lightshows.clear,
    'dummy': lightshows.dummy,
    'spinthebottle': lightshows.spinthebottle,
    'strandtest': lightshows.strandtest,
    'twocolorblend': lightshows.twocolorblend,

}
