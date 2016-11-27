"""
Helpers for MQTT
(c) 2016 Simon Leiner

A couple of helper functions (big surprise!) for MQTTControl
"""

from enum import Enum
import config as user_config
import json
import logging as log

# load user settings from config.py
conf = user_config.configuration


# information you can get out of an MQTT topic (and on which path hierarchy they are)
class TopicAspect(Enum):
    prefix = 0
    sys_name = 1
    show_name = 3
    command = 4


# get the string on a specified hierarchy level
def get_from_topic(hierarchy_level: int, topic: str) -> str:
    hierarchy = topic.split(sep="/")
    return hierarchy[hierarchy_level]


# turn a binary represented string into a python string
def binary_to_string(payload) -> str:
    string = str(payload)
    stripped_string = string[2:-1]  # remove first two and last character
    return stripped_string


def assemble_path(show_name: str, command: str, prefix: str = conf.mqtt.prefix, sys_name: str = conf.sys_name):
    path = conf.mqtt.general_path.format(prefix=prefix, sys_name=sys_name, show_name=show_name, command=command)
    return path


def parse_json_safely(payload: str):
    if payload:  # not empty
        try:
            unpacked = json.loads(payload)
        except:
            log.warning("Could not parse this payload")
            return
        else:
            if type(unpacked) is not dict:
                log.warning("This payload is not a JSON object!")
                return
        return unpacked
    else:
        log.debug("Payload is empty!")
        return {}
