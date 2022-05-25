"""Torque Entity class"""

from typing import TYPE_CHECKING
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity import DeviceInfo
from .const import DOMAIN, ATTRIBUTION

if TYPE_CHECKING:
    from .coordinator import TorqueLoggerCoordinator

class TorqueEntity(CoordinatorEntity):
    """Base Entity"""
    def __init__(self, coordinator: 'TorqueLoggerCoordinator',
    config_entry: ConfigEntry, sensor_key: str, device: DeviceInfo):
        super().__init__(coordinator)
        self.config_entry = config_entry
        self.sensor_key = sensor_key
        self._car_id = list(device.get("identifiers"))[0][1]
        self._car_name = device.get("model")
        self._attr_device_info = device
        self._attr_unique_id = f"{DOMAIN}_{config_entry.entry_id}_{self._car_id}_{sensor_key}"
        self._attr_attribution = ATTRIBUTION
        self._attr_extra_state_attributes = {
            "car": self._car_name
        }
