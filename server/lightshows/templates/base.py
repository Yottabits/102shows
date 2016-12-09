"""
Lightshow base template
(c) 2016 Simon Leiner
"""

from abc import ABCMeta, abstractmethod

import paho.mqtt.client

import mqtt.helpers
from drivers.abstract import LEDStrip


class Lightshow(metaclass=ABCMeta):
    """
    This class defines the interfaces and a few helper functions for lightshows.
    It is highly recommended to use it as your base class when writing your own show.
    """
    def __init__(self, strip: LEDStrip, conf, parameters: dict):
        # store parameters
        self.strip = strip
        self.conf = conf

        self.init_parameters()  # let the child class set its own default parameters

        # then overwrite with any directly given parameters
        parameters_valid = type(parameters) is dict

        # store given parameters
        if parameters_valid:
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
        """
        Take a parameter and store it.

        :param param_name: name of the parameter to be stored
        :param value: new value of the parameter to be stored
        :return: usually nothing
        """
        pass

    def init_parameters(self):
        """
        functions can inherit this to set their default parameters
        this function is called at initialization of a show object
        """
        pass

    class MQTTListener:
        """ Helper class for handling MQTT parameter changes"""

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
            """
            if this method is called by the show object, incoming MQTT messages will be parsed,
            given they have the path: $prefix/$sys_name/$show_name/$parameter
            $parameter and the $payload will be given to show.set_parameter($parameter, $payload)
            """
            if self.lightshow.conf.mqtt.username is not None:
                self.client.username_pw_set(self.lightshow.conf.mqtt.username, self.lightshow.conf.mqtt.password)
            self.client.connect(self.lightshow.conf.mqtt.broker.host,
                                self.lightshow.conf.mqtt.broker.port,
                                self.lightshow.conf.mqtt.broker.keepalive)


