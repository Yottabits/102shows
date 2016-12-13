"""
MQTT Control
(c) 2016 Simon Leiner
"""

import json
from multiprocessing import Process
from threading import Thread

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
        self.scheduled_show_name = None
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
        log.info("subscription on Broker {host} for {start_path} and {stop_path}".format(
            host=self.conf.MQTT.Broker.host, start_path=start_path, stop_path=stop_path))

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

            # set scheduled_show_name so that the idle show does not get started after the old show was quit:
            self.scheduled_show_name = show_name
            self.stop_running_show()  # stop any running show
            self.start_show(show_name, parameters)
            self.scheduled_show_name = None  # delete flag so idle show gets started if the show terminates by itself
        elif command == "stop":
            self.stop_show(show_name)
        else:
            log.debug("MQTTControl ignored {show}:{command}".format(show=show_name, command=command))

    def start_show(self, show_name: str, parameters: dict) -> None:
        """
        looks for a show, checks if it can run and if so, starts it in an own process
        the method waits for the process to terminate and then gets the buffer of the ended show

        :param show_name: name of the show to be started
        :param parameters: these are passed to the show
        """
        # search for show module
        if show_name not in self.conf.shows:
            log.error("Show \"{name}\" was not found!".format(name=show_name))
            return

        # initialize show object
        try:
            show = self.conf.shows[show_name](self.strip, self.conf, parameters)
            show.check_runnable()
        except (InvalidStrip, InvalidConf, InvalidParameters) as error_message:
            log.error(error_message)
            return

        # start the show
        log.info("Starting the show " + show_name)
        self.show_process = Process(target=show.start, name=show_name)
        self.show_process.start()

        # spawn thread that gets the final buffer state of the lightshow
        def wait_for_show_end():
            self.show_process.join()  # wait for the process to terminate
            self.after_show_end()
        Thread(target=wait_for_show_end, name="wait for " + show_name, daemon=True).start()

    def after_show_end(self) -> None:
        """
        clean up after a show ended:
          - synchronize the strip state
          - start idle show (not if we just got out of 'idle')

        :param ended_show_name: name of the show that just ended
        """
        self.strip.sync_down()  # get the buffer of the stopped lightshow
        if self.scheduled_show_name is None:  # run idle show if no other show is scheduled
            self.start_show("idle", {})

    def stop_show(self, show_name: str) -> None:
        """
        stops a show with a given name.
        If this show is not running, the function does nothing.

        :param show_name: name of the show to be stopped
        """
        if show_name == self.show_process.name or show_name == "all":
            self.stop_running_show()

    def stop_running_show(self, timeout_sec: int = 5) -> None:
        """
        stops any running show

        :param timeout_sec: time the show process has until it is terminated
        """
        if self.show_process.is_alive():
            os.kill(self.show_process.pid, signal.SIGINT)  # the stop signal has a handle attached to it
            self.show_process.join(timeout_sec)
            if self.show_process.is_alive():
                log.info("{show_name} is running. Terminating...".format(show_name=self.show_process.name))
                self.show_process.terminate()
        else:
            log.info("no show running; all good")

    def run(self) -> None:
        """ start the listener """
        log.info("Starting {name}".format(name=self.conf.sys_name))

        log.info("Initializing LED strip...")
        self.strip = self.conf.Strip.Driver(num_leds=self.conf.Strip.num_leds,
                                            max_clock_speed_hz=self.conf.Strip.max_clock_speed_hz)
        self.strip.set_global_brightness(self.conf.Strip.initial_brightness)  # set initial brightness from config
        self.strip.sync_up()  # to store brightness
        self.strip.show()

        log.info("Connecting to the MQTT Broker")
        client = paho.mqtt.client.Client()
        client.on_connect = self.on_connect
        client.on_message = self.on_message
        if self.conf.MQTT.username is not None:
            client.username_pw_set(self.conf.MQTT.username, self.conf.MQTT.password)
        client.connect(self.conf.MQTT.Broker.host, self.conf.MQTT.Broker.port, self.conf.MQTT.Broker.keepalive)
        log.info("{name} is ready".format(name=self.conf.sys_name))

        # start Idle show to listen for brightness changes and refresh the strip regularly
        self.start_show("idle", {})

        client.loop_forever()
        log.critical("MQTTControl.py has exited")
