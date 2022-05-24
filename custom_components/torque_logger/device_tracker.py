"""Device tracker for Torque Logger."""
import logging

from typing import final
from homeassistant.components.device_tracker.config_entry import TrackerEntity
from homeassistant.components.device_tracker.const import (
    DOMAIN,
    SOURCE_TYPE_GPS,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    ATTR_BATTERY_LEVEL,
    ATTR_GPS_ACCURACY,
    ATTR_LATITUDE,
    ATTR_LONGITUDE,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity

from .entity import TorqueEntity
from .coordinator import TorqueLoggerCoordinator
from .const import DOMAIN, ATTR_ALTITUDE, ATTR_SPEED, ATTR_GPS_TIME


_LOGGER: logging.Logger = logging.getLogger(__package__)

async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Setup device_tracker platform."""
    coordinator: TorqueLoggerCoordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    coordinator.async_add_device_tracker = async_add_entities


class TorqueDeviceTracker(TorqueEntity, TrackerEntity, RestoreEntity):
    """Represent a tracked device."""

    def __init__(self, coordinator: TorqueLoggerCoordinator,
    config_entry: ConfigEntry, device: DeviceInfo):
        super().__init__(coordinator, config_entry, "gps", device.model, None, device)
        self._data: dict = None

    @property
    def battery_level(self):
        """Return the battery level of the device."""
        return self._data.get(ATTR_BATTERY_LEVEL)

    @property
    def location_accuracy(self):
        """Return the gps accuracy of the device."""
        return self._data.get(ATTR_GPS_ACCURACY)

    @property
    def latitude(self):
        """Return latitude value of the device."""
        # Check with "get" instead of "in" because value can be None
        if self._data.get("gps"):
            return self._data["gps"][0]

        return None

    @property
    def longitude(self):
        """Return longitude value of the device."""
        # Check with "get" instead of "in" because value can be None
        if self._data.get("gps"):
            return self._data["gps"][1]

        return None

    @property
    def source_type(self):
        """Return the source type, eg gps or router, of the device."""
        return SOURCE_TYPE_GPS

    async def async_added_to_hass(self):
        """Call when entity about to be added to Home Assistant."""
        await super().async_added_to_hass()

        # Don't restore if we got set up with data.
        if self.coordinator.data:
            return

        if (state := await self.async_get_last_state()) is None:
            return

        attr = state.attributes
        self._data = {
            ATTR_LATITUDE: attr.get(ATTR_LATITUDE), 
            ATTR_LONGITUDE: attr.get(ATTR_LONGITUDE),
            ATTR_ALTITUDE: attr.get(ATTR_ALTITUDE),
            ATTR_GPS_ACCURACY: attr.get(ATTR_GPS_ACCURACY),
            ATTR_SPEED: attr.get(ATTR_SPEED),
            ATTR_GPS_TIME: attr.get(ATTR_GPS_TIME),
            ATTR_BATTERY_LEVEL: attr.get(ATTR_BATTERY_LEVEL),
        }

    @callback
    async def update_data(self, session_data: dict):
        """Mark the device as seen."""
        self._data = {
            ATTR_LATITUDE: float(session_data.get("gpslat")),
            ATTR_LONGITUDE: float(session_data.get("gpslon")),
            ATTR_ALTITUDE: float(session_data.get("gps_height", 0)),
            ATTR_GPS_ACCURACY: float(session_data.get("gps_acc", 0)),
            ATTR_SPEED: float(session_data.get("gps_spd", 0)),
            ATTR_GPS_TIME: float(session_data.get("time")),
            ATTR_BATTERY_LEVEL: None
        }
        if self.hass:
            self.async_write_ha_state()
