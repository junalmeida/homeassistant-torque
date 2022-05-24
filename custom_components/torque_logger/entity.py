"""Torque Entity class"""
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.util import slugify
from homeassistant.helpers.entity import DeviceInfo

from .coordinator import TorqueLoggerCoordinator
from .const import DOMAIN, ATTRIBUTION


class TorqueEntity(CoordinatorEntity):
    """Base Entity"""
    def __init__(self, coordinator: TorqueLoggerCoordinator,
    config_entry: ConfigEntry, sensor_key: str, sensor_name: str, unit: str, device: DeviceInfo):
        super().__init__(coordinator)
        self.config_entry = config_entry
        self.sensor_key = sensor_key
        self._name = sensor_name
        self._device = device
        self._car_id = device.get("identifiers")
        self._car_name = device.get("model")
        self._attr_name = f"{self._car_name} {sensor_name}"
        self._attr_unit_of_measurement = unit
        self._unique_id = f"{config_entry.entry_id}_{self._car_id}_{sensor_key}"

    @property
    def unique_id(self):
        """Return a unique ID to use for this entity."""
        return self._unique_id

    @property
    def device_info(self):
        return self._device

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return {
            "attribution": ATTRIBUTION,
            "id": self._car_id,
            "integration": DOMAIN,
        }
