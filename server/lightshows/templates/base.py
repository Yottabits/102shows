# Lightshow base template
# (c) 2016-2017 Simon Leiner
# licensed under the GNU Public License, version 2

from abc import ABCMeta, abstractmethod
import json
import logging
import os
import signal
import time

import paho.mqtt.client

import helpers.mqtt
import helpers.verify as verify
from drivers import LEDStrip
from helpers.configparser import get_configuration
from helpers.exceptions import *


class LightshowParameters:
    """\
    A collection of maps for the parameters which store their:
    
       - current values
       - preprocessor method references
       - verifier method references
       
    """

    def __init__(self):
        self.value = {}  #: maps the show parameter names to their current values
        self.verifier = {}  #: maps the show parameter names to their verifier functions
        self.preprocessor = {}  #: maps the show parameter names to their preprocessor functions


class Lightshow(metaclass=ABCMeta):
    """\
    This class defines the interfaces and a few helper functions for lightshows.
    It is highly recommended to use it as your base class when writing your own show.

    :param strip: A :py:class:`drivers.LEDStrip` object representing your strip
    :param parameters: A :py:class:`dict` mapping parameter names (of the lightshow) to the parameter values,
                       for example: ::

                           parameters = {'example_rgb_color': (255,127,8),
                                         'an_arbitrary_fade_time_sec': 1.5}
    """

    # Attributes
    p = None  #: The object that stores all show parameters

    logger = None  #: The logger object this show will use for debug output
    mqtt = None  #: represents the MQTT connection for parsing parameter changes #FIXME: type annotation
    strip = None  #: the object representing the LED strip (driver) #FIXME: type annotation

    def __init__(self, strip: LEDStrip, parameters: dict):
        # logger
        self.logger = logging.getLogger('102shows.server.lightshows.' + self.name)

        # MQTT listener
        self.mqtt = self.MQTTListener(self)

        # Parameters
        self.p = LightshowParameters()
        self.strip = strip
        self.init_parameters()  # let the child class set its own default parameters

        # override with any directly given parameters
        self.apply_parameter_set(parameters)

    @property
    def name(self) -> str:
        """The name of the lightshow in lower-cases"""
        subclass_name = type(self).__name__
        return subclass_name.lower()

    def start(self) -> None:
        """invokes the :py:func:`run` method and after that synchronizes the shared buffer"""
        # before
        signal.signal(signal.SIGINT, self.stop)  # attach stop() to SIGINT
        self.strip.sync_down()
        self.mqtt.start_listening()

        self.run()  # run the show

        # loop and listen to brightness changes until the end
        self.idle_forever()

    def idle_forever(self, delay_sec: float = -1) -> None:
        """\
        Just does nothing and invokes :py:func:`drivers.LEDStrip.show` until the end of time
        (or a call of :py:func:`stop`)

        :param delay_sec: Time between two calls of :py:func:`drivers.LEDStrip.show`
        """

        if delay_sec < 0:
            delay_sec = self.mqtt.global_conf.Strip.refresh_time_sec

        while True:
            self.strip.show()
            time.sleep(delay_sec)  # do not refresh in this time

    def sleep(self, time_sec: float) -> None:
        """\
        Does nothing (but refreshing the strip a few times) for ``time_sec`` seconds

        :param time_sec: duration of the break
        """
        stop_time = time.perf_counter() + time_sec  # when the delay should be over
        final_refresh = stop_time - self.strip.max_refresh_time_sec  # when show() should be invoked for the last time

        while final_refresh > time.perf_counter():  # spend (hopefully most of) the time refreshing the strip
            self.strip.show()

        while stop_time > time.perf_counter():  # wait until the end
            pass

    def stop(self, signum=None, frame=None) -> None:
        """\
        .. todo:: include link for SIGINT

        This should be called to stop the show with a graceful ending.
        It guarantees that the last strip state is uploaded to the global inter-process buffer.
        This method is called when SIGINT is sent to the show process.
        The arguments have no influence on the function.

        :param signum: The integer-code of the signal sent to the show process.
            This has no influence on how the function works.
        :param frame: #fixme
        """
        self.strip.freeze()
        self.cleanup()  # give the show a chance to clean up (but without changing the buffer)
        self.strip.sync_up()
        self.suicide()  # then kill all running threads in this process

    def suicide(self) -> None:
        """terminates its own process"""
        os.kill(os.getpid(), signal.SIGKILL)

    def register(self, parameter_name: str, default_val, verifier, args: list = None, kwargs: dict = None,
                 preprocessor=None) -> None:
        """\
        MQTT-settable parameters are stored in :py:attr:`lightshows.templates.base.Lightshow.p.value`.
        Calling this function will register a new parameter and his verifier in
        :py:attr:`~lightshows.templates.base.Lightshow.p.value` and
        :py:attr:`~lightshows.templates.base.Lightshow.p.verifier`, so the parameter can be
        set via MQTT and by the controller.

        :param parameter_name: name of the parameter. You access the parameter via self.p.value[parameter_name].
        :param default_val: initializer value of the parameter.
                            *Note that this value will not be checked by the verifier function!*
        :param verifier: a function that is called before the parameter is set via MQTT.
                         If it raises an InvalidParameters exception, the new value will not be set.  #FIXLINK
        :param args: the verifier function will be called as :samp:`{verifier}(new_value, param_name, *args, **kwargs)`
        :param kwargs: the verifier function will be called via
                       :samp:`{verifier}(new_value, param_name, *args, **kwargs)`
        :param preprocessor: before the validation in set_parameter :samp:`value = {preprocessor}(value)` will be called
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
        if parameter_name in self.p.value:
            raise InvalidParameters("Parameter {} was already registered".format(parameter_name))

        # store parameter
        self.p.value[parameter_name] = default_val
        self.p.verifier[parameter_name] = (verifier, args, kwargs)
        self.p.preprocessor[parameter_name] = preprocessor

    def apply_parameter_set(self, parameters: dict) -> None:
        """\
        Applies a set of parameters to the show.
        
        :param parameters: Parameter JSON Object, represented as a Python :py:class:`dict`
        :return: ``True`` if successful, ``False`` if not
        """
        if type(parameters) is dict:
            for param_name in parameters:
                self.set_parameter(param_name, value=parameters[param_name], send_mqtt_update=False)
            self.mqtt.send_current_parameter_state()
        else:
            print("parameters", type(parameters))
            raise InvalidParameters("Parameters payload must be given as JSON like this: " +
                                    "{\"param_name\": 42, \"param2_name\": [255,125,0]}  " +
                                    "(instead received: " + str(parameters) + " ).")

    def set_parameter(self, param_name: str, value, send_mqtt_update: bool = True) -> None:
        """\
        Take a parameter by name and new value and store it to p.value.

        :param param_name: name of the parameter to be stored
        :param value: new value of the parameter to be stored
        :param send_mqtt_update: Send the updated parameter array to the MQTT current parameter path after update
        """

        # pre-process the value
        preprocessor = self.p.preprocessor[param_name]
        value = preprocessor(value)

        try:
            verifier, args, kwargs = self.p.verifier[param_name]
            verifier(value, param_name, *args, **kwargs)  # run verifier
        except KeyError:  # param_name not found in p.verifier => unknown
            self.logger.warning("Parameter {} is unknown!".format_map(param_name))
        except InvalidParameters as error_message:  # verifier raised an exception
            self.logger.warning(error_message)
        else:
            self.p.value[param_name] = value
            if send_mqtt_update:
                self.mqtt.send_current_parameter_state()

    # next we have the abstract methods that classes MUST implement:

    @abstractmethod
    def init_parameters(self) -> None:
        """\
        Lightshows can inherit this to set their default parameters.
        This function is called at initialization of a new show object.
        """
        pass

    @abstractmethod
    def check_runnable(self):
        """\
        .. todo:: include official exception raise notice

        Raise an exception (InvalidStrip, InvalidConf or InvalidParameters) if the show is not runnable
        """
        raise NotImplementedError

    @abstractmethod
    def run(self) -> None:
        """\
        The "main" function of the show
        (obviously this must be re-implemented in child classes)
        """
        pass

    def cleanup(self) -> None:
        """\
        This is called before the show gets terminated.
        Lightshows can use it to clean up resources before their process is killed.
        """
        pass

    class MQTTListener:
        """\
        This class collects the functions that receive incoming MQTT messages
        and parse them as parameter changes.
        """

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

        def subscribe(self, client, userdata, flags, rc) -> None:
            """\
            Function to be executed as ``on_connect`` hook of the Paho MQTT client.
            It subscribes to the MQTT paths for brightness changes and parameter changes for the show.

            .. todo::
                - include link to the paho mqtt lib
                - explain currently unknown parameters

            :param client: the calling client object
            :param userdata: no idea what this does.
                This is a necessary argument but is not handled in any way in the function.
            :param flags: no idea what this does.
                This is a necessary argument but is not handled in any way in the function.
            :param rc: no idea what this does.
                This is a necessary argument but is not handled in any way in the function.
            """
            set_brightness_path = self.global_conf.MQTT.Path.global_brightness_set
            parameter_path = self.global_conf.MQTT.Path.show_parameter_set.format(show_name=self.lightshow.name)

            client.subscribe(set_brightness_path)
            self.logger.debug("show subscribed to {}".format(set_brightness_path))
            client.subscribe(parameter_path)
            self.logger.debug("show subscribed to {}".format(parameter_path))

        def parse_message(self, client, userdata, msg) -> None:
            """\
            Function to be executed as ``on_message`` hook of the Paho MQTT client.
            If the message commands a brightness or parameter change the corresponding
            hook (:py:func:`set_brightness` or :py:func:`set_parameter`) is called.

            .. todo::
                - include link to the paho mqtt lib
                - explain currently unknown parameters

            :param client: the calling client object
            :param userdata: no idea what this does.
                This is a necessary argument but is not handled in any way in the function.
            :param msg: The object representing the incoming MQTT message
            """

            if msg.topic == self.global_conf.MQTT.Path.global_brightness_set:
                try:
                    new_brightness = float(msg.payload)  # parse string to float
                except ValueError:
                    self.logger.error("Could not parse set brightness as a number!")
                    return

                try:  # verify that the number is in the defined range
                    verify.numeric(new_brightness, "brightness", minimum=0.0, maximum=1.0)
                    self.lightshow.strip.set_global_brightness(new_brightness)
                except helpers.exceptions.InvalidParameters as error_msg:
                    self.logger.error(error_msg)
                    return

                self.set_brightness(new_brightness)  # apply to the strip

            else:  # must be a show parameter
                parameters = json.loads(msg.payload.decode())

                if self.parse_parameter_changes:
                    self.lightshow.apply_parameter_set(parameters)

        def set_brightness(self, brightness: float) -> None:
            """\
            Limits the brightness value to the maximum brightness that is set in the configuration file,
            then calls the strip driver's :py:func:`drivers.LEDStrip.set_global_brightness` function
            
            :param brightness: float between 0.0 and 1.0
            """
            # confine brightness to configured value
            max_brightness = self.global_conf.Strip.max_brightness_percent / 100.0
            if brightness > max_brightness:
                self.logger.info("tried to set brightness {set} but configured maximum brightness is {max}.".format(
                    set=brightness, max=max_brightness))
                self.logger.info("setting {max} as brightness instead...".format(max=max_brightness))
                brightness = max_brightness

            # finally: set brightness of the strip
            self.lightshow.strip.set_global_brightness(brightness)

            self.client.publish(topic=self.global_conf.MQTT.Path.global_brightness_current,
                                payload=str(brightness),
                                qos=1,
                                retain=True)

        def send_current_parameter_state(self):
            path = self.global_conf.MQTT.Path.show_parameter_current.format(show_name=self.lightshow.name)
            self.client.publish(
                topic=path,
                payload=json.dumps(self.lightshow.p.value),
                qos=1,
                retain=True)

        def start_listening(self) -> None:
            """\
            If this method is called (e.g. by the show object), incoming MQTT messages will be parsed,
            given they have the path ``$prefix/$sys_name/$show_name/$parameter``
            ``$parameter`` and the ``$payload`` will be given to
            :py:func:`lightshow.templates.base.Lightshow.set_parameter`
            """
            self.client.loop_start()

        def stop_listening(self) -> None:
            """\
            Ends the connection to the MQTT broker.
            Messages from the subscribed topics are not parsed anymore.
            """
            self.client.loop_stop()
