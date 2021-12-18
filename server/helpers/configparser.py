# 102shows Configuration File Parser
# (c) 2016-2017 Simon Leiner
# licensed under the GNU Public License, version 2


from copy import deepcopy
import logging

from orderedattrdict.yamlutils import from_yaml
from orderedattrdict import AttrDict as ConfigTree
import yaml

# Load YAML always as AttrDict (aka ConfigTree)
yaml.add_constructor(u'tag:yaml.org,2002:map', from_yaml, yaml.SafeLoader)
yaml.add_constructor(u'tag:yaml.org,2002:omap', from_yaml, yaml.SafeLoader)

logger = logging.getLogger('102shows.server.helpers.configparser')


def update_settings_tree(base: ConfigTree, update: ConfigTree) -> ConfigTree:
    """
    For all attributes in ``update`` override the defaults set in ``base``
    or add them to the tree, if they did not exist in ``base``.

    :param base: default config tree
    :param update: "patch" for the default config tree

    :return: the updated tree
    """
    updated = deepcopy(base)
    for _, key in enumerate(update):
        if type(update[key]) is ConfigTree:
            if key in base:
                updated[key] = update_settings_tree(base[key], update[key])
            else:
                updated[key] = update[key]
        else:
            updated[key] = update[key]
    return updated


def get_configuration(default_filename: str = 'defaults.yml', user_filename: str = 'config.yml') -> ConfigTree:
    """
    gets the current configuration, as specified by YAML files

    :param default_filename: name of the default settings file (relative to :file:`configparser.py`)
    :param user_filename: name of the user settings file (relative to :file:`configparser.py`)

    :return: settings tree
    """

    # read defaults
    with open(default_filename, 'r') as file:
        defaults = yaml.safe_load(file)
        logger.info("Successfully parsed {} as default configuration".format(default_filename))

    with open(user_filename, 'r') as file:
        user_config = yaml.safe_load(file)
        logger.info("Successfully parsed {} as user configuration".format(user_filename))

    # apply user config over Defaults
    configuration = update_settings_tree(base=defaults, update=user_config)

    # parse MQTT path templates
    for path_name in configuration.MQTT.Path:
        path_template = configuration.MQTT.Path[path_name]
        path = path_template.format(prefix=configuration.MQTT.prefix, sys_name=configuration.sys_name)
        configuration.MQTT.Path[path_name] = path

    return configuration
