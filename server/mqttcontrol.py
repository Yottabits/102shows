"""
MQTT Control
(c) 2016 Simon Leiner
licensed under the GNU Public License, version 2

See the class description for a description of what this module does.
"""

import json
import logging
from multiprocessing import Process
import os
import signal

import paho.mqtt.client
import paho.mqtt.publish

import helpers.mqtt
from drivers.__active__ import get_driver
from helpers.exceptions import *
from helpers.configparser import ConfigTree
from helpers.mqtt import TopicAspect
from lightshows.__active__ import shows

logger = logging.getLogger('102shows.server.mqttcontrol')


class MQTTControl:
    """
    This class provides function to start/stop the shows under lightshows/
    according to the commands it receives via MQTT
    """

    def __init__(self, config: ConfigTree):
        # global handles
        self.conf = config  # the user config
        self.show_process = Process()  # for the process in which the lightshows run in
        self.strip = None  # for the LED strip

    def notify_user(self, message, qos=0) -> None:
        """
        send to the MQTT notification channel: Node-RED will display a toast notification

        :param message: the text to be displayed
        :param qos: MQTT parameter
        """
        paho.mqtt.publish.single(
            topic=self.conf.MQTT.notification_path.format(prefix=self.conf.MQTT.prefix, sys_name=self.conf.sys_name),
            payload=message,
            qos=qos,
            hostname=self.conf.MQTT.Broker.host,
            port=self.conf.MQTT.Broker.port,
            keepalive=self.conf.MQTT.Broker.keepalive
        )

    def on_connect(self, client, userdata, flags, rc):
        """ subscribe to all messages related to this LED installation """
        start_path = self.conf.MQTT.general_path.format(
            prefix=self.conf.MQTT.prefix,
            sys_name=self.conf.sys_name,
            show_name="+",
            command="start")
        stop_path = self.conf.MQTT.general_path.format(
            prefix=self.conf.MQTT.prefix,
            sys_name=self.conf.sys_name,
            show_name="+",
            command="stop")

        client.subscribe(start_path)
        client.subscribe(stop_path)
        logger.info("subscription on Broker {host} for {start_path} and {stop_path}".format(
            host=self.conf.MQTT.Broker.host, start_path=start_path, stop_path=stop_path))

    def on_message(self, client, userdata, msg):
        """ react to a received message and eventually starts/stops a show """
        # store parameters as strings
        topic = str(msg.topic)
        if type(msg.payload) is bytes:  # might be a byte encoded string that must be stripped
            payload = helpers.mqtt.binary_to_string(msg.payload)
        else:
            payload = str(msg.payload)

        # extract the essentials
        show_name = helpers.mqtt.get_from_topic(TopicAspect.show_name, topic)
        command = helpers.mqtt.get_from_topic(TopicAspect.command, topic)

        # execute
        if command == "start":
            # parse parameters
            parameters = helpers.mqtt.parse_json_safely(payload)
            logger.debug(
                """for show: \"{show}\":
                   received command: \"{command}\"
                   with:
                   {parameters}
                """.format(show=show_name,
                           command=command,
                           parameters=json.dumps(parameters, sort_keys=True, indent=8, separators=(',', ': '))
                           ))
            self.stop_running_show()  # stop any running show
            self.start_show(show_name, parameters)
        elif command == "stop":
            self.stop_show(show_name)
        else:
            logger.debug("MQTTControl ignored {show}:{command}".format(show=show_name, command=command))

    def start_show(self, show_name: str, parameters: dict) -> None:
        """
        looks for a show, checks if it can run and if so, starts it in an own process

        :param show_name: name of the show to be started
        :param parameters: these are passed to the show
        """
        # search for show module
        if show_name not in shows:
            logger.error("Show \"{name}\" was not found!".format(name=show_name))
            return

        # initialize show object
        try:
            show = shows[show_name](self.strip, parameters)
            show.check_runnable()
        except (InvalidStrip, InvalidConf, InvalidParameters) as error_message:
            logger.error(error_message)
            self.start_show('idle', {})
            return

        # start the show
        logger.info("Starting the show " + show_name)
        self.show_process = Process(target=show.start, name=show_name)
        self.show_process.start()

    def stop_show(self, show_name: str) -> None:
        """
        stops a show with a given name.
        If this show is not running, the function does nothing.

        :param show_name: name of the show to be stopped
        """
        if show_name == self.show_process.name or show_name == "all":
            self.stop_running_show()

    def stop_running_show(self, timeout_sec: float = 5) -> None:
        """
        stops any running show

        :param timeout_sec: time the show process has until it is terminated
        """
        if self.show_process.is_alive():
            os.kill(self.show_process.pid, signal.SIGINT)  # the stop signal has a handle attached to it
            self.show_process.join(timeout_sec)
            if self.show_process.is_alive():
                logger.info("{show_name} is running. Terminating...".format(show_name=self.show_process.name))
                self.show_process.terminate()
        else:
            logger.info("no show running; all good")

    def run(self) -> None:
        """ start the listener """
        logger.info("Starting {name}".format(name=self.conf.sys_name))

        logger.info("Initializing LED strip...")
        driver = get_driver(self.conf.Strip.driver)
        self.strip = driver(num_leds=self.conf.Strip.num_leds,
                            max_clock_speed_hz=self.conf.Strip.max_clock_speed_hz)
        self.strip.set_global_brightness(self.conf.Strip.initial_brightness)
        self.strip.sync_up()

        logger.info("Connecting to the MQTT Broker")
        client = paho.mqtt.client.Client()
        client.on_connect = self.on_connect
        client.on_message = self.on_message
        if self.conf.MQTT.username is not None:
            client.username_pw_set(self.conf.MQTT.username, self.conf.MQTT.password)
        client.connect(self.conf.MQTT.Broker.host, self.conf.MQTT.Broker.port, self.conf.MQTT.Broker.keepalive)
        logger.info("{name} is ready".format(name=self.conf.sys_name))

        # start a show show to listen for brightness changes and refresh the strip regularly
        self.start_show("clear", {})

        try:
            signal.signal(signal.SIGTERM, self.stop_controller)  # attach stop_controller() to SIGTERM
            client.loop_forever()
        except KeyboardInterrupt:
            self.stop_controller()
        finally:
            logger.critical("MQTTControl.py has exited")

    def stop_controller(self, signum=None, frame=None):
        """ what happens if the controller exits """
        del self.strip  # close driver connection
