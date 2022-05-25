"""
The Torque Logger integration with Home Assistant.

For more details about this integration, please refer to
https://github.com/junalmeida/homeassistant-torque#readme
"""

import logging
import asyncio

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import Config, HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .coordinator import TorqueLoggerCoordinator
from .api import TorqueReceiveDataView

from .const import (
    CONF_EMAIL,
    DOMAIN,
    PLATFORMS,
    STARTUP_MESSAGE,
)

_LOGGER: logging.Logger = logging.getLogger(__package__)

async def async_setup(*_):
    """Set up this integration using YAML is not supported."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up this integration using UI."""
    if hass.data.get(DOMAIN) is None:
        hass.data.setdefault(DOMAIN, {})
        _LOGGER.info(STARTUP_MESSAGE)

    hass.data[DOMAIN][entry.entry_id] = {}
    hass.data[DOMAIN][entry.entry_id]["data"] = {}
    email = entry.data.get(CONF_EMAIL)

    client = TorqueReceiveDataView(hass.data[DOMAIN][entry.entry_id]["data"], email, False)
    coordinator = TorqueLoggerCoordinator(hass, client, entry)
    client.coordinator = coordinator

    hass.data[DOMAIN][entry.entry_id]["coordinator"] = coordinator

    hass.http.register_view(client)

    for platform in PLATFORMS:
        hass.async_add_job(
            hass.config_entries.async_forward_entry_setup(entry, platform)
        )

    entry.async_on_unload(entry.add_update_listener(async_reload_entry))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Handle removal of an entry."""
    unloaded = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, platform)
                for platform in PLATFORMS
            ]
        )
    )
    if unloaded:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unloaded


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
