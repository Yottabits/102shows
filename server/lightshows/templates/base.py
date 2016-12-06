from abc import ABCMeta, abstractmethod
from DefaultConfig import Configuration
from drivers.apa102 import APA102 as LEDStrip
import mqtt.helpers
import paho.mqtt.client


class Lightshow(metaclass=ABCMeta):
    def __init__(self, strip: LEDStrip, conf: Configuration, parameters: dict):
        self.strip = strip
        self.conf = conf

        self.init_parameters()

        # store given parameters
        for param_name in parameters:
            self.set_parameter(param_name, parameters[param_name])

    @property
    def name(self) -> str:
        subclass_name = type(self).__name__
        return subclass_name.lower()

    @abstractmethod
    def check_runnable(self):
        """ Raise an exception (InvalidStrip, InvalidConf or InvalidParameters) if the show is not runnable"""
        raise NotImplementedError

    @abstractmethod
    def run(self):
        """Start the show with the parameters given in the constructor"""
        raise NotImplementedError

    @abstractmethod
    def set_parameter(self, param_name: str, value):
        pass

    def init_parameters(self):
        pass

    class MQTTListener:
        def __init__(self, lightshow):
            self.lightshow = lightshow
            self.client = paho.mqtt.client.Client()
            self.client.on_connect = self.subscribe_to_show
            self.client.on_message = self.store_to_parameters

        def subscribe_to_show(self, client, userdata, flags, rc):
            subscription_path = self.lightshow.conf.mqtt.general_path.format(
                prefix=self.lightshow.conf.mqtt.prefix,
                sys_name=self.lightshow.conf.sys_name,
                show_name=self.lightshow.namelightshow.conf,
                command="+")
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


class InvalidStrip(Exception):
    pass


class InvalidConf(Exception):
    pass


class InvalidParameters(Exception):
    @staticmethod
    def unknown(param_name: str = None):
        if param_name:
            debug_str = "Parameter \"{name}\" is unknown!".format(name=param_name)
        else:
            debug_str = "Parameter is unknown!"
        return InvalidParameters(debug_str)

    @staticmethod
    def missing(param_name: str = None):
        if param_name:
            debug_str = "Parameter \"{name}\" is missing!".format(name=param_name)
        else:
            debug_str = "Parameter is missing!"
        return InvalidParameters(debug_str)
