"""vtherm_climate_replication integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .climate_replication import ClimateReplication
from .const import DATA_ENABLED, DATA_PHYSICAL_CLIMATE, DATA_REPLICATION, DATA_TARGET_CLIMATE, DOMAIN, PLATFORMS


async def async_setup(hass: HomeAssistant, _: dict) -> bool:
    """Set up the integration from yaml."""
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up vtherm climate replication from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        DATA_ENABLED: True,
        DATA_PHYSICAL_CLIMATE: entry.data[DATA_PHYSICAL_CLIMATE],
        DATA_TARGET_CLIMATE: entry.data[DATA_TARGET_CLIMATE],
    }
    replication = ClimateReplication(hass, entry)
    hass.data[DOMAIN][entry.entry_id][DATA_REPLICATION] = replication
    await replication.async_setup()
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        replication = hass.data[DOMAIN][entry.entry_id][DATA_REPLICATION]
        await replication.async_unload()
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unloaded
