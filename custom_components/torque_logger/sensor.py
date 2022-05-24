"""Sensor platform for Torque Logger."""
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.core import HomeAssistant

from .coordinator import TorqueLoggerCoordinator
from .const import DOMAIN, DEFAULT_ICON
from .entity import TorqueEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry,
    async_add_devices: AddEntitiesCallback):
    """Setup sensor platform."""
    coordinator: TorqueLoggerCoordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    coordinator.async_add_sensor = async_add_devices

class TorqueSensor(TorqueEntity, SensorEntity, RestoreEntity):
    """Torque Sensor class."""

    @property
    def native_value(self):
        """Return the native value of the sensor."""
        return self.coordinator.data.get(self.sensor_key)

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return DEFAULT_ICON
