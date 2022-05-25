"""Torque Logger Coordinator."""
import logging
from typing import TYPE_CHECKING

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.util import slugify

from .sensor import TorqueSensor
from .device_tracker import TorqueDeviceTracker
from .const import DOMAIN, ENTITY_GPS

if TYPE_CHECKING:
    from .api import TorqueReceiveDataView

_LOGGER: logging.Logger = logging.getLogger(__package__)

class TorqueLoggerCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    async_add_sensor: AddEntitiesCallback
    async_add_device_tracker: AddEntitiesCallback
    tracked: list[str] = list()

    def __init__(self,
    hass: HomeAssistant, client: 'TorqueReceiveDataView',
    entry: ConfigEntry) -> None:
        """Initialize."""
        self.api = client
        self.entry = entry
        client.coordinator = self

        super().__init__(hass, _LOGGER, name=DOMAIN)

    async def _async_update_data(self):
        _LOGGER.debug("no-op")

    async def add_entities(self, session_data: dict):
        """Add not tracked entities"""
        car_id = slugify(session_data["profile"]["Name"])
        car_name = session_data["profile"]["Name"]
        device = DeviceInfo(
            identifiers={(DOMAIN, car_id, "car")},
            manufacturer="Torque", #TODO: Get car manufacturer
            model=car_name,
            name=car_name,
            sw_version=session_data["profile"].get("version")
        )

        new_sensors: list['TorqueSensor'] = list()
        new_trackers: list['TorqueDeviceTracker'] = list()
        for key, _ in session_data["meta"].items():
            sensor_name = session_data["meta"][key].get("name")
            unit = session_data["meta"][key].get("unit", "").strip()
            if (sensor_name != "" and sensor_name != key and len(unit) > 0 and
                key[0:3] != ENTITY_GPS and key not in self.tracked):
                # do not publish until we have sensor name and unit
                sensor = TorqueSensor(self, self.entry, key, device)
                new_sensors.append(sensor)

        if "gpslat" in session_data and "gpslon" in session_data and ENTITY_GPS not in self.tracked:
            sensor = TorqueDeviceTracker(self, self.entry, device)
            new_trackers.append(sensor)
        if len(new_sensors) > 0:
            self.tracked.extend([x.sensor_key for x in new_sensors])
            self.async_add_sensor(new_sensors)
        if len(new_trackers) > 0:
            self.tracked.extend([x.sensor_key for x in new_trackers])
            self.async_add_device_tracker(new_trackers)
        _LOGGER.debug(", ".join(self.tracked))
