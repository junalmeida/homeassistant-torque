"""Constants for Torque Logger"""
# Base component constants
from typing import Final
import json
import os


NAME: Final = "Torque Logger"
DOMAIN: Final = "torque_logger"
_manifest = os.path.join(os.path.dirname(__file__), "manifest.json")
with open(_manifest, encoding="utf-8") as file:
    VERSION: Final = json.load(file)["version"]
ATTRIBUTION: Final = "Data provided by Torque Pro"
ISSUE_URL: Final = "https://github.com/junalmeida/homeassistant-torque/issues"

# CONF
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
DEFAULT_ICON: Final = "mdi:engine"
GPS_ICON: Final = "mdi:car"
DISTANCE_ICON: Final = "mdi:map-marker-distance"
HIGHWAY_ICON: Final = "mdi:highway"
FUEL_ICON: Final = "mdi:gas-station"
TIME_ICON: Final = "mdi:clock"
CITY_ICON: Final = "mdi:city"
SPEED_ICON: Final = "mdi:speedometer"

# ATTR
ATTR_ALTITUDE: Final = "altitude"
ATTR_SPEED: Final = "speed"
ATTR_GPS_TIME: Final = "gps_time"

ENTITY_GPS: Final = "gps"

TORQUE_GPS_LAT: Final = "gpslat"
TORQUE_GPS_LON: Final = "gpslon"
TORQUE_GPS_ALTITUDE: Final = "gps_height"
TORQUE_GPS_ACCURACY: Final = "gps_acc"
