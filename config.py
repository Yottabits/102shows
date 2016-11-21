from lightshows import *

general_settings = {
    "mqtt":
        {
            # broker
            "host": "localhost",
            "port": 1883,
            "keepalive": 60,

            # structure
            "prefix": "led",
            "id": "couch",
            "stdout_path": "notification",
        }
}

shows = {
    #'clear':         clear,
    #'spinthebottle': spinthebottle,
    #'strandtest':    strandtest,
    #'twocolorblend': twocolorblend,
    'dummy':          dummy
}