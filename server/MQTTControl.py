# from apa102 import APA102 @rpi
from DummyAPA102 import APA102
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
from multiprocessing import Process
import lightshows
import json
import helpers
from helpers import TopicAspect
import config as user_config

# load user settings from config.py
conf = user_config.configuration

# load available lightshows
shows = user_config.shows

# global handles
show_process = Process()  # for the process in which the lightshows run in
strip = None  # for the APA102 LED strip


# send to the MQTT notification channel: Node-RED will display a toast notification
def notify_user(message, qos=0):
    publish.single(
        topic=conf.mqtt.notification_path.format(prefix=conf.mqtt.prefix, sys_name=conf.sys_name),
        payload=message,
        qos=qos,
        hostname=conf.mqtt.broker.host,
        port=conf.mqtt.broker.port,
        keepalive=conf.mqtt.broker.keepalive
    )


def debug_msg(msg):
    print(msg)


# subscribe to all messages related to this LED installation
def on_connect(client, userdata, flags, rc):
    subscription_path = helpers.assemble_path(show_name="+", command="+")
    client.subscribe(subscription_path)

    debug_msg("subscription on broker {host} for {path}".format(host=conf.mqtt.broker.host, path=subscription_path))


def on_message(client, userdata, msg):
    # store parameters as strings
    topic = str(msg.topic)
    if type(msg.payload) is bytes:  # might be a byte encoded string that must be stripped
        payload = helpers.binary_to_string(msg.payload)
    else:
        payload = str(msg.payload)

    # extract the essentials
    show_name = helpers.get_from_topic(TopicAspect.show_name.value, topic)
    command = helpers.get_from_topic(TopicAspect.command.value, topic)
    if payload:  # not empty
        try:
            parameters = json.loads(payload)
        except:
            debug_msg("Could not parse payload!")
            return
        else:
            if type(parameters) is not dict:
                debug_msg("Please supply a JSON object as payload!")
                return
    else:
        debug_msg("payload is empty!")
        parameters = {}

    debug_msg(
        """for show: \"{show}\":
            received command: \"{command}\"
         """.format(show=show_name,
                   command=command,
                   #parameters=json.dumps(parameters, sort_keys=True, indent=8, separators=(',', ': '))
                    ))

    if command == "stop":  # parameter: timeout (as integer in seconds)
        if "timeout" in parameters:
            stop_running_show(parameters["timeout"])
        else:
            stop_running_show()

    elif command == "start":  # parameter: show name
        stop_running_show()
        start_show(show_name, parameters)


def stop_running_show(timeout_sec: int = 5):
    global show_process
    if not show_process.is_alive():
        debug_msg("no show running")
    else:
        show_process.join(timeout_sec)


def start_show(show_name: str, parameters: dict):
    # search for show module
    if show_name in user_config.shows:
        show = user_config.shows[show_name]
    else:
        debug_msg("Show {name} was not found!".format(name=show_name))
        return

    # check for valid parameters
    if not show.parameters_valid(parameters):
        debug_msg("invalid parameters sent!")
        return

    global show_process, strip
    arguments = {"strip": strip, "conf": conf, "parameters": parameters}
    show_process = Process(target=show.run, name="lightshow-" + show_name, kwargs=arguments)
    show_process.start()


def run() -> None:
    global show_process, strip

    debug_msg("Starting {name}".format(name=conf.sys_name))

    debug_msg("Initializing LED strip...")
    strip = APA102(conf.strip.num_leds, conf.strip.global_brightness, 'rgb', conf.strip.max_spi_speed_hz)
    strip.verbose = True  # @nopi

    debug_msg("Connecting to the MQTT broker")
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(conf.mqtt.broker.host, conf.mqtt.broker.port, conf.mqtt.broker.keepalive)
    debug_msg("{name} is ready".format(name=conf.sys_name))

    client.loop_forever()
    debug_msg("MQTTControl.py has exited")

if __name__ == '__main__':
    run()
