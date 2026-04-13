"""Replication controller for vtherm_climate_replication."""

from __future__ import annotations

from collections.abc import Callable

from homeassistant.components.climate import ClimateEntityFeature, DOMAIN as CLIMATE_DOMAIN
from homeassistant.components.climate.const import (
    ATTR_HVAC_MODE,
    ATTR_PRESET_MODE,
    PRESET_NONE,
    SERVICE_SET_HVAC_MODE,
    SERVICE_SET_PRESET_MODE,
    SERVICE_SET_TEMPERATURE,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE
from homeassistant.core import Event, EventStateChangedData, HomeAssistant, State, callback
from homeassistant.helpers.entity_component import EntityComponent
from homeassistant.helpers.event import async_track_state_change_event
from vtherm_api import PluginClimate

from .const import DATA_ENABLED, DATA_PHYSICAL_CLIMATE, DATA_TARGET_CLIMATE, DOMAIN


class ClimateReplication:
    """Replicate physical climate changes to a linked VTherm entity."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the replication controller."""
        self._hass = hass
        self._entry = entry
        self._plugin = PluginClimate(hass)
        self._remove_state_listener: Callable[[], None] | None = None

    async def async_setup(self) -> None:
        """Start the replication controller."""
        self._link_to_target_vtherm()
        self._remove_state_listener = async_track_state_change_event(
            self._hass,
            self._physical_climate_entity_id,
            self._handle_physical_climate_change,
        )

    async def async_unload(self) -> None:
        """Stop the replication controller."""
        if self._remove_state_listener is not None:
            self._remove_state_listener()
            self._remove_state_listener = None
        self._plugin.remove_listeners()

    async def async_resync_target_climate_state(self) -> None:
        """Synchronize the linked VTherm with the current physical climate state."""
        physical_state = self._hass.states.get(self._physical_climate_entity_id)
        if physical_state is None:
            return

        if not self._link_to_target_vtherm():
            return

        await self._async_apply_hvac_mode(physical_state)
        await self._async_apply_preset(physical_state)
        await self._async_apply_target_temperature(physical_state)

    @property
    def _runtime_data(self) -> dict:
        """Return the runtime data for this config entry."""
        return self._hass.data[DOMAIN][self._entry.entry_id]

    @property
    def _enabled(self) -> bool:
        """Return whether replication is enabled."""
        return self._runtime_data[DATA_ENABLED]

    @property
    def _physical_climate_entity_id(self) -> str:
        """Return the source climate entity id."""
        return self._runtime_data[DATA_PHYSICAL_CLIMATE]

    @property
    def _target_climate_entity_id(self) -> str:
        """Return the target VTherm entity id."""
        return self._runtime_data[DATA_TARGET_CLIMATE]

    def _link_to_target_vtherm(self) -> bool:
        """Attach PluginClimate to the configured VTherm entity when available."""
        linked_vtherm = self._plugin.linked_vtherm
        if getattr(linked_vtherm, "entity_id", None) == self._target_climate_entity_id:
            return True

        component: EntityComponent | None = self._hass.data.get(CLIMATE_DOMAIN)
        if component is None:
            return False

        vtherm = component.get_entity(self._target_climate_entity_id)
        if vtherm is None:
            return False

        self._plugin.link_to_vtherm(vtherm)
        return True

    @callback
    def _handle_physical_climate_change(
        self,
        event: Event[EventStateChangedData],
    ) -> None:
        """Schedule replication when the physical climate changes."""
        self._hass.async_create_task(self._async_handle_physical_climate_change(event))

    async def _async_handle_physical_climate_change(
        self,
        event: Event[EventStateChangedData],
    ) -> None:
        """Replicate the relevant state changes to the linked VTherm."""
        if not self._enabled:
            return

        old_state = event.data.get("old_state")
        new_state = event.data.get("new_state")
        if old_state is None or new_state is None:
            return

        if not self._link_to_target_vtherm():
            return

        await self._async_replicate_hvac_mode(old_state, new_state)
        await self._async_replicate_preset(old_state, new_state)
        await self._async_replicate_target_temperature(old_state, new_state)

    async def _async_replicate_hvac_mode(self, old_state: State, new_state: State) -> None:
        """Replicate HVAC mode changes."""
        old_hvac_mode = old_state.attributes.get(ATTR_HVAC_MODE, old_state.state)
        new_hvac_mode = new_state.attributes.get(ATTR_HVAC_MODE, new_state.state)
        if old_hvac_mode == new_hvac_mode or new_hvac_mode is None:
            return

        await self._async_apply_hvac_mode(new_state)

    async def _async_apply_hvac_mode(self, state: State) -> None:
        """Apply the HVAC mode from the provided state to the linked VTherm."""
        hvac_mode = state.attributes.get(ATTR_HVAC_MODE, state.state)
        if hvac_mode is None:
            return

        await self._plugin.call_linked_vtherm_action(
            SERVICE_SET_HVAC_MODE,
            {ATTR_HVAC_MODE: hvac_mode},
        )

    async def _async_replicate_preset(self, old_state: State, new_state: State) -> None:
        """Replicate preset changes."""
        old_preset = old_state.attributes.get(ATTR_PRESET_MODE)
        new_preset = new_state.attributes.get(ATTR_PRESET_MODE)
        if old_preset == new_preset:
            return

        await self._async_apply_preset(new_state)

    async def _async_apply_preset(self, state: State) -> None:
        """Apply the preset from the provided state to the linked VTherm."""
        linked_vtherm = self._plugin.linked_vtherm
        if not linked_vtherm or not (linked_vtherm.supported_features & ClimateEntityFeature.PRESET_MODE):
            return

        preset_mode = state.attributes.get(ATTR_PRESET_MODE)

        await self._plugin.call_linked_vtherm_action(
            SERVICE_SET_PRESET_MODE,
            {ATTR_PRESET_MODE: preset_mode or PRESET_NONE},
        )

    async def _async_replicate_target_temperature(self, old_state: State, new_state: State) -> None:
        """Replicate target temperature changes."""
        old_temperature = old_state.attributes.get(ATTR_TEMPERATURE)
        new_temperature = new_state.attributes.get(ATTR_TEMPERATURE)
        if old_temperature == new_temperature or new_temperature is None:
            return

        await self._async_apply_target_temperature(new_state)

    async def _async_apply_target_temperature(self, state: State) -> None:
        """Apply the target temperature from the provided state to the linked VTherm."""
        temperature = state.attributes.get(ATTR_TEMPERATURE)
        if temperature is None:
            return

        await self._plugin.call_linked_vtherm_action(
            SERVICE_SET_TEMPERATURE,
            {ATTR_TEMPERATURE: temperature},
        )
