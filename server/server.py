"""
102shows server
(C) 2016 Simon Leiner

This script just starts the server.
The real magic does not happen here, though.
"""

import logging as log

import config
from mqttcontrol import MQTTControl

user_config = config.configuration  # load the configuration
log.getLogger().setLevel(user_config.log_level)  # set the log level
server = MQTTControl(user_config)  # initialize the server...
server.run()  # ... and off we go!
