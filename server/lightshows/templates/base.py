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
import lightshows.utilities.verifyparameters as verify
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
        self.mqtt = self.MQTTListener(self)

        # initialize stop signal variable
        self.__synced_stop_signal = SyncedValue('b', False)
        self.__stop_watchdog_thread = Thread(target=self.stop_watchdog, daemon=True)

        self.init_parameters()  # let the child class set its own default parameters

        # then overwrite with any directly given parameters
        parameters_valid = type(parameters) is dict

        # store given parameters
        if parameters_valid:
            for param_name in parameters:
                self.set_parameter(param_name, parameters[param_name])

    def stop_watchdog(self):
        while True:
            if self.__synced_stop_signal.value:  # stop signal was set!

                self.strip.freeze()
                sleep(0.01)  # wait for any running buffer-changing activity to terminate

                self.cleanup()  # give the show a chance to clean up (but without changing the buffer)
                self.strip.sync_up()

                self.__synced_stop_signal.value = False  # reset the stop signal
                return
            sleep(0.05)  # give the processor some rest

    @property
    def name(self) -> str:
        subclass_name = type(self).__name__
        return subclass_name.lower()

    @abstractmethod
    def check_runnable(self):
        """ Raise an exception (InvalidStrip, InvalidConf or InvalidParameters) if the show is not runnable"""
        raise NotImplementedError

    def start(self):
        """ invokes the run() method and after that synchronizes the shared buffer """
        # before
        self.strip.sync_down()
        self.__stop_watchdog_thread.start()
        self.mqtt.start_listening()

        self.run()  # run the show

        self.cleanup()
        self.strip.freeze()
        self.strip.sync_up()

    def stop(self) -> None:
        """
        sends stop signal to itself

        this is usually necessary because stop() is called from the controller ("parent") process,
        but start() is called from the show ("child") process
        """
        self.__synced_stop_signal.value = True

    @abstractmethod
    def run(self):
        """ run the show (obviously this must be inherited) """
        pass

    def cleanup(self):
        """ called before the show is terminated """
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
            self.client.on_connect = self.subscribe
            self.client.on_message = self.parse_message
            self.parse_parameter_changes = False

        def subscribe(self, client, userdata, flags, rc):
            brightness_path = self.lightshow.conf.mqtt.general_path.format(
                prefix=self.lightshow.conf.MQTTMQTTfix,
                sys_name=self.lightshow.conf.sys_name,
                show_name="+",
                command="brightness")
            parameter_path = self.lightshow.conf.mqtt.general_path.format(
                prefix=self.lightshow.conf.MQTTMQTTfix,
                sys_name=self.lightshow.conf.sys_name,
                show_name=self.lightshow.name,
                command="+")

            client.subscribe(brightness_path)
            log.debug("show subscribed to {}".format(brightness_path))
            client.subscribe(parameter_path)
            log.debug("show subscribed to {}".format(parameter_path))

        def parse_message(self, client, userdata, msg):
            command = mqtt.helpers.get_from_topic(mqtt.helpers.TopicAspect.command, str(msg.topic))
            if type(msg.payload) is bytes:  # might be a byte encoded string that must be stripped
                payload = mqtt.helpers.binary_to_string(msg.payload)
            else:
                payload = str(msg.payload)

            if command == "brightness":
                self.set_brightness(payload)
            else:
                if self.parse_parameter_changes:
                    self.lightshow.set_parameter(command, payload)

        def set_brightness(self, payload: str) -> None:
            """
            try to cast the payload as an integer between 0 and 100,
            then invoke the strip's set_global_brightness()

            :param payload: string containing the brightness as integer
            """
            try:
                brightness = int(payload)
            except ValueError:
                log.error("Could not parse set brightness as integer!")
                return
            try:
                verify.integer(brightness, "brightness", minimum=0, maximum=100)
            except verify.InvalidParameters as error_msg:
                log.error(error_msg)
                return
            self.lightshow.strip.set_global_brightness(brightness)

        def start_listening(self) -> None:
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

        def stop_listening(self) -> None:
            """
            ends the connection to the MQTT broker
            the subscribed topics are not parsed anymore
            """
            self.client.disconnect()


