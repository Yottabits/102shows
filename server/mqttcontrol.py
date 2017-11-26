# MQTT Control
# (c) 2016-2017 Simon Leiner
# licensed under the GNU Public License, version 2

"""\
This module starts the central MQTT listener and manages all the lightshows.
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
    """\
    This class provides function to start/stop the shows under lightshows/
    according to the commands it receives via MQTT
    """

    def __init__(self, config: ConfigTree):
        # global handles
        self.conf = config  # the user config
        self.show_process = Process()  # for the process in which the lightshows run in
        self.strip = None  # for the LED strip

        # MQTT client
        self.mqtt = paho.mqtt.client.Client()
        self.mqtt.on_connect = self.on_connect
        self.mqtt.on_message = self.on_message

    def notify_user(self, message, qos=0) -> None:
        """\
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
        """subscribe to all messages related to this LED installation"""
        start_path = self.conf.MQTT.Path.show_start
        stop_path = self.conf.MQTT.Path.show_stop

        client.subscribe(start_path)
        client.subscribe(stop_path)
        logger.info("subscription on Broker {host} for {start_path} and {stop_path}".format(
            host=self.conf.MQTT.Broker.host, start_path=start_path, stop_path=stop_path))

    def on_message(self, client, userdata, msg):
        """react to a received message and eventually starts/stops a show"""
        # store parameters as strings
        topic = str(msg.topic)
        if type(msg.payload) is bytes:  # might be a byte encoded string that must be stripped
            payload = msg.payload.decode()
        else:
            payload = str(msg.payload)

        # logging the MQTT message
        logger.debug(
            "Incoming MQTT message: \n" +
            "topic:   {}".format(topic) + ";   " +
            "payload: {}".format(payload)
        )

        if topic == self.conf.MQTT.Path.show_start:

            # parse payload
            payload_tree = helpers.mqtt.parse_json_safely(payload)
            show_name = payload_tree['name']
            try:
                parameters = payload_tree['parameters']
            except KeyError:
                parameters = {}

            # logging
            logger.info("MQTT command interpreted: START the show \"{}\" (with given parameters: {} ).".format(
                show_name, parameters))

            self.stop_running_show()  # stop any running show
            self.start_show(show_name, parameters)  # start the new show

        elif topic == self.conf.MQTT.Path.show_stop:

            # logging
            logger.info("MQTT command interpreted: STOP the running show")
            self.stop_running_show()

    def start_show(self, show_name: str, parameters: dict) -> None:
        """\
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
            self.start_show('clear', {})
            return

        # start the show
        logger.info("Starting the show " + show_name)
        self.show_process = Process(target=show.start, name=show_name)
        self.show_process.start()

        # propagate via MQTT
        self.mqtt.publish(topic=self.conf.MQTT.Path.show_current,
                          payload=show_name,
                          qos=1,
                          retain=True)

    def stop_show(self, show_name: str) -> None:
        """\
        stops a show with a given name.
        If this show is not running, the function does nothing.

        :param show_name: name of the show to be stopped
        """
        if show_name == self.show_process.name or show_name == "all":
            self.stop_running_show()

    def stop_running_show(self, timeout_sec: float = 1) -> None:
        """\
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
            logger.debug("no show running; nothing to stop")

        # propagate via MQTT
        self.mqtt.publish(topic=self.conf.MQTT.Path.show_current,
                          payload="",
                          qos=1,
                          retain=True)

    def run(self) -> None:
        """start the listener"""
        logger.info("Starting {name}".format(name=self.conf.sys_name))

        logger.info("Initializing LED strip...")
        driver = get_driver(self.conf.Strip.driver)
        self.strip = driver(num_leds=self.conf.Strip.num_leds,
                            max_clock_speed_hz=self.conf.Strip.max_clock_speed_hz,
                            max_global_brightness=self.conf.Strip.max_brightness_percent / 100.0)
        self.strip.set_global_brightness(self.conf.Strip.initial_brightness_percent / 100.0)
        self.strip.sync_up()

        logger.info("Connecting to the MQTT Broker")
        if self.conf.MQTT.username is not None:
            self.mqtt.username_pw_set(self.conf.MQTT.username, self.conf.MQTT.password)
        self.mqtt.connect(self.conf.MQTT.Broker.host, self.conf.MQTT.Broker.port, self.conf.MQTT.Broker.keepalive)
        logger.info("{name} is ready".format(name=self.conf.sys_name))

        # start a show show to listen for brightness changes and refresh the strip regularly
        self.start_show("clear", {})

        try:
            signal.signal(signal.SIGTERM, self.stop_controller)  # attach stop_controller() to SIGTERM
            self.mqtt.loop_forever()
        except KeyboardInterrupt:
            self.stop_controller()
        finally:
            logger.critical("MQTTControl.py has exited")

    def stop_controller(self, signum=None, frame=None):
        """what happens if the controller exits"""
        del self.strip  # close driver connection
