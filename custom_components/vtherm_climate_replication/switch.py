"""Switch platform for vtherm_climate_replication."""

from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity

from .const import DATA_ENABLED, DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the switch for a config entry."""
    async_add_entities([ReplicationEnabledSwitch(hass, entry)])


class ReplicationEnabledSwitch(RestoreEntity, SwitchEntity):
    """Switch controlling whether climate replication is enabled."""

    _attr_icon = "mdi:content-copy"

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the switch."""
        self.hass = hass
        self._entry = entry
        self._attr_unique_id = entry.entry_id
        self._attr_name = f"{entry.title} replication"
        self._attr_is_on = hass.data[DOMAIN][entry.entry_id][DATA_ENABLED]

    async def async_added_to_hass(self) -> None:
        """Restore the previous switch state."""
        await super().async_added_to_hass()
        if (last_state := await self.async_get_last_state()) is not None:
            self._set_enabled(last_state.state == "on")

    async def async_turn_on(self, **kwargs) -> None:
        """Turn the switch on."""
        self._set_enabled(True)
        self.async_write_ha_state()

    def turn_on(self, **kwargs) -> None:
        """Turn the switch on synchronously."""
        raise HomeAssistantError("Synchronous turn_on is not supported")

    async def async_turn_off(self, **kwargs) -> None:
        """Turn the switch off."""
        self._set_enabled(False)
        self.async_write_ha_state()

    def turn_off(self, **kwargs) -> None:
        """Turn the switch off synchronously."""
        raise HomeAssistantError("Synchronous turn_off is not supported")

    def _set_enabled(self, enabled: bool) -> None:
        """Persist the enabled flag in runtime data."""
        self._attr_is_on = enabled
        self.hass.data[DOMAIN][self._entry.entry_id][DATA_ENABLED] = enabled