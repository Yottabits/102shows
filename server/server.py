import mqtt.MQTTControl
import config

user_config = config.configuration

mqtt.MQTTControl.run(user_config)
