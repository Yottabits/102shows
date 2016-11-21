import DefaultConfig
import lightshows

# load default configuration
configuration = DefaultConfig.Configuration()

# set your own parameters here
configuration.sys_name = "couch"
configuration.strip.num_leds = 4  # @nopi 576


shows = {
    'clear': lightshows.clear,
    # 'spinthebottle': spinthebottle,
    # 'strandtest':    strandtest,
    # 'twocolorblend': twocolorblend,
    'dummy': lightshows.dummy
}
