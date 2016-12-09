"""
102shows server
(C) 2016 Simon Leiner

This script just starts the server.
The real magic does not happen here, though.
"""

import mqtt.MQTTControl
import config
import logging as log

user_config = config.configuration  # load the configuration
log.getLogger().setLevel(user_config.log_level)  # set the log level
server = mqtt.MQTTControl.MQTTControl(user_config)  # initialize the server...
server.run()  # ... and of we go!
