"""
Lightshow base template
(c) 2016 Simon Leiner
licensed under the GNU Public License, version 2
"""

import logging
import os
import signal
import time
from abc import ABCMeta, abstractmethod

import paho.mqtt.client

import helpers.mqtt
import helpers.verify as verify
from drivers import LEDStrip
from helpers.configparser import get_configuration
from helpers.exceptions import *


class Lightshow(metaclass=ABCMeta):
    """
    This class defines the interfaces and a few helper functions for lightshows.
    It is highly recommended to use it as your base class when writing your own show.
    """

    def __init__(self, strip: LEDStrip, parameters: dict):
        # logger
        self.logger = logging.getLogger('102shows.server.lightshows.' + self.name)

        # MQTT listener
        self.mqtt = self.MQTTListener(self)

        # Parameters
        self.strip = strip
        self.p = {}  # dict: parameter_name => value
        self.p_verifier = {}  # dict: parameter_name => (verifier_function, args, kwargs)
        self.p_preprocessor = {}  # dict: parameter_name => preprocessor_function
        self.init_parameters()  # let the child class set its own default parameters

        # override with any directly given parameters
        parameters_valid = type(parameters) is dict
        if parameters_valid:
            for param_name in parameters:
                self.set_parameter(param_name, parameters[param_name])

    @property
    def name(self) -> str:
        subclass_name = type(self).__name__
        return subclass_name.lower()

    def start(self):
        """ invokes the run() method and after that synchronizes the shared buffer """
        # before
        signal.signal(signal.SIGINT, self.stop)  # attach stop() to SIGINT
        self.strip.sync_down()
        self.mqtt.start_listening()

        self.run()  # run the show

        # loop and listen to brightness changes until the end
        self.idle_forever()

    def idle_forever(self, delay_sec: float = 0.1):
        """ just idling and invoking strip.show() every now and then"""
        while True:
            self.strip.show()
            time.sleep(delay_sec)  # do not refresh in this time

    def sleep(self, time_sec: float) -> None:
        """
        does nothing (but refreshing the strip a few times) for time_sec seconds

        :param time_sec: duration of the break
        """
        stop_time = time.perf_counter() + time_sec  # when the delay should be over
        final_refresh = stop_time - self.strip.max_refresh_time_sec  # when show() should be invoked for the last time

        while final_refresh > time.perf_counter():  # spend (hopefully most of) the time refreshing the strip
            self.strip.show()

        while stop_time > time.perf_counter():  # wait until the end
            pass

    def stop(self, signum, frame) -> None:
        self.strip.freeze()
        self.cleanup()  # give the show a chance to clean up (but without changing the buffer)
        self.strip.sync_up()
        self.suicide()  # then kill all running threads in this process

    def suicide(self) -> None:
        """ terminates its own process """
        os.kill(os.getpid(), signal.SIGKILL)

    def register(self, parameter_name: str, default_val, verifier: callable, args: list = None, kwargs: dict = None,
                 preprocessor: callable = None) -> None:
        """
        MQTT-settable parameters are stored in self.p
        Calling this function will register a new parameter and his verifier in p and p_verifier,
        so the parameter can be set via MQTT and by the controller.

        :param parameter_name: name of the parameter. You access the parameter via self.p[parameter_name]
        :param default_val: initializer value of the parameter. Note that this value will not be checked!
        :param verifier: a function that is called before the parameter is set via MQTT. If it raises an
                         InvalidParameters exception, the new value will not be set
        :param args: the verifier function will be called via verifier(new_value, param_name, *args, **kwargs)
        :param kwargs: the verifier function will be called via verifier(new_value, param_name, *args, **kwargs)
        :param preprocessor: before the validation in set_parameter value = preprocessor(value) will be called
        """

        # cast None to empty iterables
        if args is None:
            args = []
        if kwargs is None:
            kwargs = {}

        # standard preprocessor
        def empty_preprocessor(val):
            return val

        if preprocessor is None:
            preprocessor = empty_preprocessor

        # check if already registered
        if parameter_name in self.p:
            raise InvalidParameters("Parameter {} was already registered".format(parameter_name))

        # store parameter
        self.p[parameter_name] = default_val
        self.p_verifier[parameter_name] = (verifier, args, kwargs)
        self.p_preprocessor[parameter_name] = preprocessor

    def set_parameter(self, param_name: str, value) -> None:
        """
        Take a parameter by name and new value and store it to p.

        :param param_name: name of the parameter to be stored
        :param value: new value of the parameter to be stored
        """

        # pre-process the value
        preprocessor = self.p_preprocessor[param_name]
        value = preprocessor(value)

        try:
            verifier, args, kwargs = self.p_verifier[param_name]
            verifier(value, param_name, *args, **kwargs)  # run verifier
        except KeyError:  # param_name not found in p_verifier => unknown
            self.logger.warning("Parameter {} is unknown!".format_map(param_name))
        except InvalidParameters as error_message:  # verifier raised an exception
            self.logger.warning(error_message)
        else:
            self.p[param_name] = value

    # next we have the abstract methods that classes MUST implement:

    @abstractmethod
    def init_parameters(self):
        """
        functions can inherit this to set their default parameters
        this function is called at initialization of a show object
        """
        pass

    @abstractmethod
    def check_runnable(self):
        """ Raise an exception (InvalidStrip, InvalidConf or InvalidParameters) if the show is not runnable"""
        raise NotImplementedError

    @abstractmethod
    def run(self):
        """ run the show (obviously this must be inherited) """
        pass

    def cleanup(self):
        """ called before the show is terminated """
        pass

    class MQTTListener:
        """ Helper class for handling MQTT parameter changes"""

        def __init__(self, lightshow):
            self.logger = logging.getLogger('102shows.server.lightshows.{}.MQTTListener'.format(lightshow.name))
            self.lightshow = lightshow
            self.global_conf = get_configuration()
            self.client = paho.mqtt.client.Client()
            self.client.on_connect = self.subscribe
            self.client.on_message = self.parse_message
            self.parse_parameter_changes = False

            # connect
            if self.global_conf.MQTT.username is not None:
                self.client.username_pw_set(self.global_conf.MQTT.username, self.global_conf.MQTT.password)
            self.client.connect(self.global_conf.MQTT.Broker.host,
                                self.global_conf.MQTT.Broker.port,
                                self.global_conf.MQTT.Broker.keepalive)

        def subscribe(self, client, userdata, flags, rc):
            brightness_path = self.global_conf.MQTT.general_path.format(
                prefix=self.global_conf.MQTT.prefix,
                sys_name=self.global_conf.sys_name,
                show_name="+",
                command="brightness")
            parameter_path = self.global_conf.MQTT.general_path.format(
                prefix=self.global_conf.MQTT.prefix,
                sys_name=self.global_conf.sys_name,
                show_name=self.lightshow.name,
                command="+")

            client.subscribe(brightness_path)
            self.logger.debug("show subscribed to {}".format(brightness_path))
            client.subscribe(parameter_path)
            self.logger.debug("show subscribed to {}".format(parameter_path))

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
                self.logger.error("Could not parse set brightness as integer!")
                return
            try:
                verify.integer(brightness, "brightness", minimum=0, maximum=100)
            except helpers.exceptions.InvalidParameters as error_msg:
                self.logger.error(error_msg)
                return

            # confine brightness to configured value
            max_brightness = self.global_conf.Strip.max_brightness
            if brightness > max_brightness:
                self.logger.info("tried to set brightness {set} but maximum brightness is {max}.".format(
                    set=brightness, max=max_brightness))
                self.logger.info("setting {max} as brightness instead...".format(max=max_brightness))
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
