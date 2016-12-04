from abc import ABCMeta, abstractmethod
from DefaultConfig import Configuration
from drivers.apa102 import APA102 as LEDStrip
import mqtt.helpers
import paho.mqtt.client as paho


class Lightshow(metaclass=ABCMeta):
    def __init__(self, strip: LEDStrip, conf: Configuration, parameters: dict):
        self.strip = strip
        self.conf = Configuration
        self.parameters = parameters

    @property
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def runnable(self) -> bool:
        """ Check if there are enough LEDs in the strip, if the parameters and configuration are valid... """
        raise NotImplementedError

    @abstractmethod
    def run(self):
        """Start the show with the parameters given in the constructor"""
        raise NotImplementedError

    def set_parameter(self, parameter: str, value):
        pass

    class MQTTListener:
        def __init__(self, lightshow):
            self.lightshow = lightshow
            self.client = paho.Client()
            self.client.on_connect = self.subscribe_to_show
            self.client.on_message = self.store_to_parameters

        def subscribe_to_show(self, client, userdata, flags, rc):
            subscription_path = mqtt.helpers.assemble_path(show_name=self.lightshow.name, command="+")
            client.subscribe(subscription_path)

        def store_to_parameters(self, client, userdata, msg):
            command = mqtt.helpers.get_from_topic(mqtt.helpers.TopicAspect.command, str(msg.topic))
            if type(msg.payload) is bytes:  # might be a byte encoded string that must be stripped
                payload = mqtt.helpers.binary_to_string(msg.payload)
            else:
                payload = str(msg.payload)
            self.lightshow.set_parameter(command, payload)

        def start(self):
            if self.lightshow.conf.mqtt.username is not None:
                self.client.username_pw_set(self.lightshow.conf.mqtt.username, self.lightshow.conf.mqtt.password)
            self.client.connect(self.lightshow.conf.mqtt.broker.host,
                                self.lightshow.conf.mqtt.broker.port,
                                self.lightshow.conf.mqtt.broker.keepalive)
