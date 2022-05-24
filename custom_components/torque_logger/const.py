"""Constants for Torque Logger"""
# Base component constants
from typing import Final


NAME = "Torque Logger"
DOMAIN = "torque_logger"
DOMAIN_DATA = f"{DOMAIN}_data"
VERSION = "1.0.0"
ATTRIBUTION = "Data provided by Torque Pro"
ISSUE_URL = "https://github.com/junalmeida/homeassistant-torque/issues"

#CONF
CONF_EMAIL = "email"
CONF_IMPERIAL = "imperial"

# Platforms
BINARY_SENSOR = "binary_sensor"
SENSOR = "sensor"
PLATFORMS = [SENSOR]

STARTUP_MESSAGE = f"""
-------------------------------------------------------------------
{NAME}
Version: {VERSION}
This is a custom integration!
If you have any issues with this you need to open an issue here:
{ISSUE_URL}
-------------------------------------------------------------------
"""

# DEFAULTs
DEFAULT_ICON = "mdi:engine"
GPS_ICON = "mdi:car"

# ATTR
ATTR_ALTITUDE: Final = "altitude"
ATTR_SPEED: Final = "speed"
ATTR_GPS_TIME: Final = "gps_time"
