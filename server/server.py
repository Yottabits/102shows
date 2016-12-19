"""
102shows server
(C) 2016 Simon Leiner

This script just starts the server.
The real magic does not happen here, though.

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation in version 2.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License along
with this program; if not, write to the Free Software Foundation, Inc.,
51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
"""

import logging

import coloredlogs

from helpers.configparser import get_configuration
from mqttcontrol import MQTTControl

# configuration
user_config = get_configuration()

# logger
logger = logging.getLogger('102shows.server')
coloredlogs.install(level=user_config.log_level)

# start the server!
server = MQTTControl(user_config)  # initialize the server...
server.run()  # ... and off we go!
