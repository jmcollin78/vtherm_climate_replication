"""Tests for config entry setup."""

from __future__ import annotations

from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.vtherm_climate_replication.const import (
    DATA_ENABLED,
    DATA_PHYSICAL_CLIMATE,
    DATA_TARGET_CLIMATE,
    DOMAIN,
)


async def test_setup_entry_creates_switch_entity(hass) -> None:
    """Setting up an entry should create the replication switch."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Physical -> VTherm",
        data={
            DATA_PHYSICAL_CLIMATE: "climate.physical",
            DATA_TARGET_CLIMATE: "climate.vtherm",
        },
    )
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    state = hass.states.get("switch.physical_vtherm_replication")
    assert state is not None
    assert state.state == "on"
    assert hass.data[DOMAIN][entry.entry_id][DATA_ENABLED] is True

    registry = er.async_get(hass)
    entity_entry = registry.async_get("switch.physical_vtherm_replication")
    assert entity_entry is not None
    assert entity_entry.unique_id == entry.entry_id


async def test_unload_entry_removes_runtime_data(hass) -> None:
    """Unloading an entry should clean up runtime data."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Physical -> VTherm",
        data={
            DATA_PHYSICAL_CLIMATE: "climate.physical",
            DATA_TARGET_CLIMATE: "climate.vtherm",
        },
    )
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    assert await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()

    assert entry.entry_id not in hass.data[DOMAIN]