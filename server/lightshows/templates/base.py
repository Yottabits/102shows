"""
Lightshow base template
(c) 2016 Simon Leiner
"""

from abc import ABCMeta, abstractmethod
import logging as log
from threading import Thread
from time import sleep
from multiprocessing import Value as SyncedValue

import paho.mqtt.client

import mqtt.helpers
from drivers import LEDStrip


class Lightshow(metaclass=ABCMeta):
    """
    This class defines the interfaces and a few helper functions for lightshows.
    It is highly recommended to use it as your base class when writing your own show.
    """
    def __init__(self, strip: LEDStrip, conf, parameters: dict):
        # store parameters
        self.strip = strip
        self.conf = conf

        # MQTT listener
        self.mqtt_listener = self.MQTTListener(self)

        # initialize stop signal variable
        self.synced_stop_signal = None
        self.stop_watchdog_thread = Thread(target=self.stop_watchdog, daemon=True)

        self.init_parameters()  # let the child class set its own default parameters

        # then overwrite with any directly given parameters
        parameters_valid = type(parameters) is dict

        # store given parameters
        if parameters_valid:
            for param_name in parameters:
                self.set_parameter(param_name, parameters[param_name])

    def init_stop_signal(self, signal: SyncedValue):
        self.synced_stop_signal = signal
        self.stop_watchdog_thread.start()

    def stop_watchdog(self):
        while True:
            if self.synced_stop_signal.value:
                self.stop()
                self.synced_stop_signal.value = False
                return
            sleep(0.1)

    @property
    def name(self) -> str:
        subclass_name = type(self).__name__
        return subclass_name.lower()

    @abstractmethod
    def check_runnable(self):
        """ Raise an exception (InvalidStrip, InvalidConf or InvalidParameters) if the show is not runnable"""
        raise NotImplementedError

    def writes_buffer(self, function):
        def wrapper():
            function()
            self.strip.write_buffer()
        return wrapper

    def start(self):
        """ invokes the run() method and after that synchronizes the shard buffer """
        self.run()
        self.strip.write_buffer()

    def stop(self):
        """ Other classes can call this method to stop the lightshow """
        log.warning("This Lightshow does not implement a stop() method")

    @abstractmethod
    def run(self):
        """ run the show (obviously this must be inherited) """
        pass

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
                prefix=self.lightshow.conf.MQTTMQTTfix,
                sys_name=self.lightshow.conf.sys_name,
                show_name=self.lightshow.name,
                command="+")
            client.subscribe(subscription_path)
            log.debug("show subscribed to {}".format(subscription_path))

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
            if self.lightshow.conf.MQTT.username is not None:
                self.client.username_pw_set(self.lightshow.conf.MQTT.username, self.lightshow.conf.MQTT.password)
            self.client.connect(self.lightshow.conf.MQTT.Broker.host,
                                self.lightshow.conf.MQTT.Broker.port,
                                self.lightshow.conf.MQTT.Broker.keepalive)


