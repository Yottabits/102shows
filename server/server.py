"""
102shows server
(C) 2016 Simon Leiner

This script just starts the server.
The real magic does not happen here, though.
"""

import logging

import coloredlogs

from helpers.configparser import get_configuration
from mqttcontrol import MQTTControl

# configuration
user_config = get_configuration()

# logger
logger = logging.getLogger('102shows.server')
coloredlogs.install(level=user_config.log_level)

# start the server!
server = MQTTControl(user_config)  # initialize the server...
server.run()  # ... and off we go!
