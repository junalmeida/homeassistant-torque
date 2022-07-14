"""Sensor platform for Torque Logger."""

import logging
import re
from typing import TYPE_CHECKING
from homeassistant.components.sensor import RestoreSensor
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers import entity_registry, device_registry

from .const import (
    CITY_ICON, DISTANCE_ICON, DOMAIN,
    DEFAULT_ICON, FUEL_ICON, HIGHWAY_ICON, SENSOR, SPEED_ICON,
    TIME_ICON)
from .entity import TorqueEntity

if TYPE_CHECKING:
    from .coordinator import TorqueLoggerCoordinator


_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup_entry(
        hass: HomeAssistant, entry: ConfigEntry,
        async_add_entities: AddEntitiesCallback):
    """Setup sensor platform."""
    coordinator: 'TorqueLoggerCoordinator' = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    coordinator.async_add_sensor = async_add_entities

    # Restore previously loaded sensors
    ent_reg = entity_registry.async_get(hass)
    dev_reg = device_registry.async_get(hass)
    devices = [
        device
        for device in dev_reg.devices.values()
        for identifier in device.identifiers
        if identifier[0] == DOMAIN
    ]
    logmsg = f"{len(devices)} devices"
    _LOGGER.debug(logmsg)

    for device in devices:
        car_id = list(device.identifiers)[0][1]
        device_info = DeviceInfo(
            identifiers=device.identifiers,
            manufacturer=device.manufacturer,
            model=device.model,
            name=device.name,
            sw_version=device.sw_version
        )
        restore_entities = [
            TorqueSensor(coordinator, entry,
                         sensor.entity_id[len(SENSOR) + len(car_id) + 2:len(sensor.entity_id)],
                         device_info)
            for sensor in ent_reg.entities.values()
            if sensor.device_id == device.id and sensor.domain == SENSOR
        ]
        logmsg = f"Restoring {', '.join([sensor.entity_id for sensor in restore_entities])}"
        _LOGGER.debug(logmsg)
        async_add_entities(restore_entities)


class TorqueSensor(TorqueEntity, RestoreSensor):
    """Torque Sensor class."""

    def __init__(self, coordinator: 'TorqueLoggerCoordinator',
                 config_entry: ConfigEntry, sensor_key: str, device: DeviceInfo):
        super().__init__(coordinator, config_entry, sensor_key, device)

        if self.coordinator.data is not None and "meta" in self.coordinator.data and self.sensor_key in self.coordinator.data["meta"]:
            self._attr_native_unit_of_measurement = (self.coordinator
                                                     .data["meta"][self.sensor_key]["unit"])
            sensor_name = self.coordinator.data["meta"].get(self.sensor_key)["name"]
            self._attr_name = sensor_name
            self._set_icon()

        self.entity_id = f"{SENSOR}.{self._car_id}_{sensor_key}"
        self._restored_state = None

    @property
    def native_value(self):
        """Return the native value of the sensor."""
        if self.coordinator.data is not None and self.sensor_key in self.coordinator.data:
            return round(float(self.coordinator.data[self.sensor_key]), 2)
        elif self._restored_state is not None:
            return round(float(self._restored_state))
        else:
            return None

    async def async_added_to_hass(self) -> None:
        """Handle entity which will be added."""
        await super().async_added_to_hass()
        state = await self.async_get_last_state()
        native_state = await self.async_get_last_sensor_data()
        if not state or not native_state:
            return
        logmsg = f"Restore state of {self.entity_id} to {native_state}"
        _LOGGER.debug(logmsg)
        self._restored_state = native_state.native_value
        self._attr_name = state.name
        self._attr_native_unit_of_measurement = native_state.native_unit_of_measurement
        self._set_icon()

    def _set_icon(self) -> None:
        self._attr_icon = DEFAULT_ICON
        if re.search('kilometers', self._attr_name, re.IGNORECASE) or re.search('miles', self._attr_name, re.IGNORECASE):
            self._attr_icon = DISTANCE_ICON
        if re.search('litre', self._attr_name, re.IGNORECASE) or re.search('gallon', self._attr_name, re.IGNORECASE):
            self._attr_icon = FUEL_ICON
        if re.search('distance', self._attr_name, re.IGNORECASE):
            self._attr_icon = DISTANCE_ICON
        if re.search('time', self._attr_name, re.IGNORECASE) or re.search('idle', self._attr_name, re.IGNORECASE):
            self._attr_icon = TIME_ICON
        if re.search('highway', self._attr_name, re.IGNORECASE):
            self._attr_icon = HIGHWAY_ICON
        if re.search('city', self._attr_name, re.IGNORECASE):
            self._attr_icon = CITY_ICON
        if re.search('speed', self._attr_name, re.IGNORECASE):
            self._attr_icon = SPEED_ICON
