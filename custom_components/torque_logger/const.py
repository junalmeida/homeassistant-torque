"""Constants for Torque Logger"""
# Base component constants
from typing import Final
import json


NAME: Final = "Torque Logger"
DOMAIN: Final = "torque_logger"
with open("manifest.json", encoding="utf-8") as file:
    VERSION: Final = json.load(file)["version"]
ATTRIBUTION: Final = "Data provided by Torque Pro"
ISSUE_URL: Final = "https://github.com/junalmeida/homeassistant-torque/issues"

#CONF
CONF_EMAIL: Final = "email"
CONF_IMPERIAL: Final = "imperial"

# Platforms
DEVICE_TRACKER: Final = "device_tracker"
SENSOR: Final = "sensor"
PLATFORMS: Final = [SENSOR, DEVICE_TRACKER]

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
