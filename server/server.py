import mqtt.MQTTControl
import config
import logging as log

# set your log level here
log.getLogger().setLevel(log.DEBUG)

user_config = config.configuration
mqtt.MQTTControl.run(user_config)
