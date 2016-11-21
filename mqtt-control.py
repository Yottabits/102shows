######## MQTT SCHEME ##########
# led/<sys-id>/show/<show>/<command>

import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
from multiprocessing import Process
import lightshows
import json
from enum import Enum
import config as user_config

# load user settings from config.py
pref = user_config.general_settings

# load available lighshows
shows = user_config.shows

# handle for the process in which the lightshows run in
show_process = Process()

# information you can get out of an MQTT topic
Topic_Aspect = Enum("id", "show", "command")


# send to the MQTT notification channel: Node-RED will display a toast notification
def notify_user(message, qos=0):
    publish.single(
        topic=pref["mqtt"]["prefix"] + "/" + pref["mqtt"]["id"] + "/" + pref["mqtt"]["stdout_path"],
        payload=message,
        qos=qos,
        hostname=pref["mqtt"]["host"],
        port=pref["mqtt"]["port"],
        keepalive=pref["mqtt"]["keepalive"]
    )


def debug_msg(msg):
    notify_user(message=msg, qos=1)


def on_connect(client, userdata, flags, rc):
    debug_msg("successfully connected to the MQTT server {host}...".format(host=pref["mqtt"]["host"]))

    # subscribe to all messages related to this LED installtion
    client.subscribe(pref["mqtt"]["prefix"] + "/" + pref["mqtt"]["id"] + "/show/+")


def on_message(client, userdata, msg):
    # extract the essentials
    show_name = get_from_topic(Topic_Aspect.show, msg.topic)
    command = get_from_topic(Topic_Aspect.command, msg.topic)
    parameters = json.loads(msg.payload)

    debug_msg(
        """for show: \"{show}\":
            received command: \"{command}\"
            with parameters:
                {parameters}

        """.format(show=show_name,
                   command=command,
                   parameters=json.dumps(parameters, sort_keys=True, indent=8, separators=(',', ': '))))

    if command == "stop":  # parameter: timeout (as integer in seconds)
        if "timeout" in parameters:
            stop_running_show(parameters["timeout"])
        else:
            stop_running_show()

    elif command == "start":  # parameter: show name
        stop_running_show()
        start_show(show_name, parameters)


def get_from_topic(aspect: str, topic: Topic_Aspect) -> str:
    _, id, _, show, command = topic.split(sep="/")

    if aspect == Topic_Aspect.id:
        return id
    elif aspect == Topic_Aspect.show:
        return show
    elif aspect == Topic_Aspect.command:
        return command


def stop_running_show(timeout_sec: int = 5):
    global show_process
    show_process.join(timeout_sec)


def start_show(show_name: str, parameters: dict):
    show_runner = lightshows.dummy.run

    global show_process
    show_process = Process(target=show_runner, name="lightshow-" + show_name, kwargs=parameters)
    show_process.start()


if True:
    debug_msg("Starting {name}".format(name=pref["mqtt"]["id"]))
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(pref["mqtt"]["host"], pref["mqtt"]["port"], pref["mqtt"]["keepalive"])
    client.loop_forever()
    print("loop exited")
