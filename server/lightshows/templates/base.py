"""
Lightshow base template
(c) 2016 Simon Leiner
"""

import logging as log
import os
import signal
from abc import ABCMeta, abstractmethod

import paho.mqtt.client

import helpers.exceptions
import helpers.mqtt
import helpers.verify as verify
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

        # attach stop() to SIGSTOP
        signal.signal(signal.SIGINT, self.stop)

        # Parameters
        self.init_parameters()  # let the child class set its own default parameters
        parameters_valid = type(parameters) is dict  # then overwrite with any directly given parameters
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

    def start(self):
        """ invokes the run() method and after that synchronizes the shared buffer """
        # before
        self.strip.sync_down()
        self.mqtt.start_listening()

        self.run()  # run the show

        self.cleanup()
        self.strip.freeze()
        self.strip.sync_up()

    def stop(self, signum, frame) -> None:
        self.strip.freeze()
        self.cleanup()  # give the show a chance to clean up (but without changing the buffer)
        self.strip.sync_up()
        self.suicide()  # then kill all running threads in this process

    def suicide(self) -> None:
        """ terminates its own process """
        os.kill(os.getpid(), signal.SIGKILL)

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

            # connect
            if self.lightshow.conf.MQTT.username is not None:
                self.client.username_pw_set(self.lightshow.conf.MQTT.username, self.lightshow.conf.MQTT.password)
            self.client.connect(self.lightshow.conf.MQTT.Broker.host,
                                self.lightshow.conf.MQTT.Broker.port,
                                self.lightshow.conf.MQTT.Broker.keepalive)

        def subscribe(self, client, userdata, flags, rc):
            brightness_path = self.lightshow.conf.MQTT.general_path.format(
                prefix=self.lightshow.conf.MQTT.prefix,
                sys_name=self.lightshow.conf.sys_name,
                show_name="+",
                command="brightness")
            parameter_path = self.lightshow.conf.MQTT.general_path.format(
                prefix=self.lightshow.conf.MQTT.prefix,
                sys_name=self.lightshow.conf.sys_name,
                show_name=self.lightshow.name,
                command="+")

            client.subscribe(brightness_path)
            log.debug("show subscribed to {}".format(brightness_path))
            client.subscribe(parameter_path)
            log.debug("show subscribed to {}".format(parameter_path))

        def parse_message(self, client, userdata, msg):
            command = helpers.mqtt.get_from_topic(helpers.mqtt.TopicAspect.command, str(msg.topic))
            if type(msg.payload) is bytes:  # might be a byte encoded string that must be stripped
                payload = helpers.mqtt.binary_to_string(msg.payload)
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

            # check general restrictions
            try:
                brightness = int(payload)
            except ValueError:
                log.error("Could not parse set brightness as integer!")
                return
            try:
                verify.integer(brightness, "brightness", minimum=0, maximum=100)
            except helpers.exceptions.InvalidParameters as error_msg:
                log.error(error_msg)
                return

            # confine brightness to configured value
            max_brightness = self.lightshow.conf.Strip.max_brightness
            if brightness > max_brightness:
                log.info("tried to set brightness {set} but maximum brightness is {max}.".format(
                    set=brightness, max=max_brightness))
                log.info("setting {max} as brightness instead...".format(max=max_brightness))
                brightness = max_brightness

            # finally: set brightness
            self.lightshow.strip.set_global_brightness(brightness)

        def start_listening(self) -> None:
            """
            if this method is called by the show object, incoming MQTT messages will be parsed,
            given they have the path: $prefix/$sys_name/$show_name/$parameter
            $parameter and the $payload will be given to show.set_parameter($parameter, $payload)
            """
            self.client.loop_start()

        def stop_listening(self) -> None:
            """
            ends the connection to the MQTT broker
            the subscribed topics are not parsed anymore
            """
            self.client.loop_stop()
