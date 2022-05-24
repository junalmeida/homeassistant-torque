"""Torque Logger Coordinator."""

import logging
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.util import slugify

from .sensor import TorqueSensor
from .device_tracker import TorqueDeviceTracker

from .api import TorqueReceiveDataView
from .entity import TorqueEntity
from .const import DOMAIN

_LOGGER: logging.Logger = logging.getLogger(__package__)

class TorqueLoggerCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    async_add_sensor: AddEntitiesCallback
    async_add_device_tracker: AddEntitiesCallback
    tracked: list[TorqueEntity] = list()

    def __init__(self,
    hass: HomeAssistant, client: TorqueReceiveDataView,
    entry: ConfigEntry) -> None:
        """Initialize."""
        self.api = client
        self.entry = entry
        client.coordinator = self

        super().__init__(hass, _LOGGER, name=DOMAIN)

    async def add_entities(self, session_data: dict):
        """Add not tracked entities"""
        car_id = slugify(session_data["profile"]["Name"])
        car_name = session_data["profile"]["Name"]
        device: DeviceInfo = {
            "identifiers": car_id,
            "manufacturer": "Torque", # TODO: Get manufacturer
            "model": car_name,
            "name": car_name,
            "sw_version": session_data["profile"].get("version")
        }

        new_sensors: list[TorqueEntity] = list()
        new_trackers: list[TorqueDeviceTracker] = list()
        for key in session_data["meta"].items():
            sensor_name = session_data["meta"][key].get("name")
            if (sensor_name != "" and sensor_name != key and
                key[0:3] != "gps" and
                key not in self.tracked):
                # do not publish until we have sensor name
                unit = session_data["meta"][key].get("unit")
                sensor = TorqueSensor(self, self.entry, key, sensor_name, unit, device)
                new_sensors.append(sensor)

        if "gpslat" in session_data and "gpslon" in session_data and "gpslat" not in self.tracked:
            sensor = TorqueDeviceTracker(self, self.entry, device)
            new_trackers.append(sensor)

        if new_sensors.count() > 0:
            self.tracked.extend([x.sensor_key for x in new_sensors])
            await self.async_add_sensor(new_sensors)
        if new_trackers.count() > 0:
            self.tracked.extend([x.sensor_key for x in new_trackers])
            await self.async_add_sensor(new_trackers)
