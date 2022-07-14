"""Device tracker for Torque Logger."""

from typing import TYPE_CHECKING
import logging

from homeassistant.components.device_tracker.config_entry import TrackerEntity
from homeassistant.components.device_tracker.const import (
    DOMAIN,
    SOURCE_TYPE_GPS,
)
from homeassistant.const import (
    ATTR_LATITUDE,
    ATTR_LONGITUDE,
    ATTR_GPS_ACCURACY
)


from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers import device_registry

from .entity import TorqueEntity
from .const import (ATTR_ALTITUDE, DOMAIN, ENTITY_GPS, GPS_ICON,
     TORQUE_GPS_ACCURACY, TORQUE_GPS_LAT,
     TORQUE_GPS_LON)
if TYPE_CHECKING:
    from .coordinator import TorqueLoggerCoordinator

_LOGGER: logging.Logger = logging.getLogger(__package__)

async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Setup device_tracker platform."""
    coordinator: 'TorqueLoggerCoordinator' = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    coordinator.async_add_device_tracker = async_add_entities

    # Restore previously loaded trackers
    dev_reg = device_registry.async_get(hass)
    devices = [
        device
        for device in dev_reg.devices.values()
        for identifier in device.identifiers
        if identifier[0] == DOMAIN
    ]
    logmsg = f"{len(devices)} device_tracker to restore"
    _LOGGER.debug(logmsg)
    for device in devices:
        logmsg = f"Restoring {device.model} device_tracker"
        device_info = DeviceInfo(
            identifiers=device.identifiers,
            manufacturer=device.manufacturer,
            model=device.model,
            name=device.name,
            sw_version=device.sw_version
        )
        _LOGGER.debug(logmsg)
        async_add_entities([TorqueDeviceTracker(coordinator, entry, device_info)])

class TorqueDeviceTracker(TorqueEntity, TrackerEntity, RestoreEntity):
    """Represent a tracked device."""

    def __init__(self, coordinator: 'TorqueLoggerCoordinator',
    config_entry: ConfigEntry, device: DeviceInfo):
        super().__init__(coordinator, config_entry, ENTITY_GPS, device)
        self._attr_name = self._car_name
        self._attr_icon = GPS_ICON
        self._restored_state: dict = None

    @property
    def battery_level(self):
        """Return the battery level of the device."""
        return None

    @property
    def location_accuracy(self):
        """Return the gps accuracy of the device."""
        if self.coordinator.data is not None and TORQUE_GPS_ACCURACY in self.coordinator.data and self.coordinator.data[TORQUE_GPS_ACCURACY] is not None:
            return float(self.coordinator.data[TORQUE_GPS_ACCURACY])
        elif self._restored_state is not None and ATTR_GPS_ACCURACY in self._restored_state and self._restored_state[ATTR_GPS_ACCURACY] is not None:
            return float(self._restored_state[ATTR_GPS_ACCURACY])
        else:
            return None
    @property
    def latitude(self):
        """Return latitude value of the device."""
        if self.coordinator.data is not None and TORQUE_GPS_LAT in self.coordinator.data and self.coordinator.data[TORQUE_GPS_LAT] is not None:
            return float(self.coordinator.data[TORQUE_GPS_LAT])
        elif self._restored_state is not None and ATTR_LATITUDE in self._restored_state and self._restored_state[ATTR_LATITUDE] is not None:
            return float(self._restored_state[ATTR_LATITUDE])
        else:
            return None
    @property
    def longitude(self):
        """Return longitude value of the device."""
        if self.coordinator.data is not None and TORQUE_GPS_LON in self.coordinator.data and self.coordinator.data[TORQUE_GPS_LON] is not None:
            return float(self.coordinator.data[TORQUE_GPS_LON])
        elif self._restored_state is not None and ATTR_LONGITUDE in self._restored_state and self._restored_state[ATTR_LONGITUDE] is not None:
            return float(self._restored_state[ATTR_LONGITUDE])
        else:
            return None

    @property
    def source_type(self):
        """Return the source type, eg gps or router, of the device."""
        return SOURCE_TYPE_GPS

    async def async_added_to_hass(self):
        """Call when entity about to be added to Home Assistant."""
        await super().async_added_to_hass()
        state = await self.async_get_last_state()
        if state is None:
            _LOGGER.debug(f"No previous state for {self.entity_id}")
            return

        attr = state.attributes
        _LOGGER.debug(f"Restored state for {self.entity_id}")
        self._restored_state = {
            ATTR_ALTITUDE: attr.get(ATTR_ALTITUDE),
            ATTR_LATITUDE: attr.get(ATTR_LATITUDE),
            ATTR_LONGITUDE: attr.get(ATTR_LONGITUDE),
            ATTR_GPS_ACCURACY: attr.get(ATTR_GPS_ACCURACY)
        }
