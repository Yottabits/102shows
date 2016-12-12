"""
MQTT Control
(c) 2016 Simon Leiner
"""

import json
import logging as log
from multiprocessing import Process
from multiprocessing import Value as SyncedValue
import threading
import time

import paho.mqtt.client
import paho.mqtt.publish

from mqtt.helpers import TopicAspect
import mqtt.helpers as helpers
from DefaultConfig import Configuration
from lightshows.templates.base import *
from lightshows.utilities.verifyparameters import InvalidStrip, InvalidConf, InvalidParameters


class MQTTControl:
    """
    This class provides function to start/stop the shows under lightshows/
    according to the commands it receives via MQTT
    """
    def __init__(self, config: Configuration):
        # global handles
        self.conf = config  # the user config
        self.show_process = Process()  # for the process in which the lightshows run in
        self.strip = None  # for the LED strip
        self.synced_stop_signal = SyncedValue('b', False)

        # initialize Anti Glitch Thread
        self.multishow_sync_thread = threading.Thread(target=self.run_synchronizer, daemon=True)
        self.multishow_sync_active = self.conf.MultiShowSync.active
        self.multishow_sync_delay_sec = self.conf.MultiShowSync.delay_sec

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
        subscription_path = self.conf.MQTT.general_path.format(
            prefix=self.conf.MQTT.prefix,
            sys_name=self.conf.sys_name,
            show_name="+",
            command="+")
        client.subscribe(subscription_path)
        log.info("subscription on Broker {host} for {path}".format(
            host=self.conf.MQTT.Broker.host, path=subscription_path))

    def on_message(self, client, userdata, msg):
        """ react to a received message and eventually starts/stops a show """
        # store parameters as strings
        topic = str(msg.topic)
        if type(msg.payload) is bytes:  # might be a byte encoded string that must be stripped
            payload = helpers.binary_to_string(msg.payload)
        else:
            payload = str(msg.payload)

        # extract the essentials
        show_name = helpers.get_from_topic(TopicAspect.show_name, topic)
        command = helpers.get_from_topic(TopicAspect.command, topic)

        # execute
        if command == "start":
            # parse parameters
            parameters = helpers.parse_json_safely(payload)
            log.debug(
                """for show: \"{show}\":
                   received command: \"{command}\"
                   with:
                   {parameters}
                """.format(show=show_name,
                           command=command,
                           parameters=json.dumps(parameters, sort_keys=True, indent=8, separators=(',', ': '))
                           ))
            self.stop_running_show(timeout_sec=0)  # stop any running show
            self.start_show(show_name, parameters)
        elif command == "stop":
            self.stop_show(show_name)
        elif command == "brightness":
            self.set_strip_brightness(int(payload))
            self.strip.sync_up()
        else:
            log.debug("MQTTControl ignored {show}:{command}".format(show=show_name, command=command))

    def run_synchronizer(self):
        """
        This function should be called periodically to write the buffer to the strip.
        That is useful for cases where plugging or unplugging another electric device
        in the room induces a glitch in the LED strip. This glitch will be visible
        until the next call of strip.show(). Because of that it is useful to write the
        buffer to the strip every now and then.
        """
        while self.multishow_sync_active:
            if not self.show_process.is_alive():  # execute only if no lightshow is running
                log.debug("synchronizing...")
                self.strip.sync_down()
                self.strip.show()
                time.sleep(self.multishow_sync_delay_sec)

    def start_show(self, show_name: str, parameters: dict) -> None:
        """
        looks for a show, checks if it can run
        and if so, starts it in an own process

        :param show_name: name of the show to be started
        :param parameters: these are passed to the show
        """
        # search for show module
        if show_name not in self.conf.shows:
            log.error("Show \"{name}\" was not found!".format(name=show_name))
            return

        try:
            show = self.conf.shows[show_name](self.strip, self.conf, parameters)
            show.check_runnable()
        except (InvalidStrip, InvalidConf, InvalidParameters) as error_message:
            log.error(error_message)
            return

        self.synced_stop_signal.value = False  # Reset the stop signal

        log.info("Starting the show " + show_name)
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

    def stop_running_show(self, timeout_sec: int = 0.7) -> None:
        """
        stops any running show

        :param timeout_sec: time the show process has until it is terminated
        """
        if self.show_process.is_alive():
            self.synced_stop_signal.value = True  # send the stop signal
            self.show_process.join(timeout_sec)
            if self.show_process.is_alive():
                log.info("{show_name} is running. Terminating...".format(show_name=self.show_process.name))
                self.show_process.terminate()
        else:
            log.info("no show running; all good")

    def set_strip_brightness(self, brightness: int) -> None:
        """
        set brightness for the whole strip

        :param brightness: integer between 0 and 100
        """
        if type(brightness) is not int or brightness < 0 or brightness > self.conf.Strip.max_brightness:
            log.warning("set brightness value \"{brightness}\" is not an integer between 0 and {max_brightness}".format(
                brightness=brightness, max_brightness=self.conf.Strip.max_brightness))
            return
        else:
            self.strip.set_global_brightness(brightness)
            self.strip.show()

    def run(self) -> None:
        """ start the listener """
        log.info("Starting {name}".format(name=self.conf.sys_name))

        log.info("Initializing LED strip...")
        self.strip = self.conf.Strip.Driver(num_leds=self.conf.Strip.num_leds,
                                            max_clock_speed_hz=self.conf.Strip.max_clock_speed_hz)
        self.strip.set_global_brightness(self.conf.Strip.initial_brightness)  # set initial brightness from config
        self.multishow_sync_thread.start()

        log.info("Connecting to the MQTT Broker")
        client = paho.mqtt.client.Client()
        client.on_connect = self.on_connect
        client.on_message = self.on_message
        if self.conf.MQTT.username is not None:
            client.username_pw_set(self.conf.MQTT.username, self.conf.MQTT.password)
        client.connect(self.conf.MQTT.Broker.host, self.conf.MQTT.Broker.port, self.conf.MQTT.Broker.keepalive)
        log.info("{name} is ready".format(name=self.conf.sys_name))

        client.loop_forever()
        log.critical("MQTTControl.py has exited")
