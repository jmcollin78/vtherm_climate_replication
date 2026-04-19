"""Tests for the climate replication controller."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, call, patch

from homeassistant.components.climate import ClimateEntityFeature
from homeassistant.components.climate.const import (
    DOMAIN as CLIMATE_DOMAIN,
    ATTR_HVAC_MODE,
    ATTR_PRESET_MODE,
    SERVICE_SET_HVAC_MODE,
    SERVICE_SET_PRESET_MODE,
    SERVICE_SET_TEMPERATURE,
    HVACMode,
)
from homeassistant.const import ATTR_ENTITY_ID, ATTR_TEMPERATURE
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.vtherm_climate_replication.const import (
    DATA_PHYSICAL_CLIMATE,
    DATA_TARGET_CLIMATE,
    DOMAIN,
)


class FakeVtherm:
    """Minimal linked VTherm entity for tests."""

    def __init__(self, entity_id: str, supported_features: int = ClimateEntityFeature.PRESET_MODE) -> None:
        self.entity_id = entity_id
        self.supported_features = supported_features


class FakeClimateComponent:
    """Minimal climate entity component exposing get_entity."""

    def __init__(self, entity) -> None:
        self._entity = entity

    def get_entity(self, entity_id: str):
        if entity_id == self._entity.entity_id:
            return self._entity
        return None


async def test_physical_climate_changes_are_replicated(hass) -> None:
    """State changes on the physical thermostat should be forwarded to the VTherm."""
    fake_vtherm = FakeVtherm("climate.vtherm")
    hass.data[CLIMATE_DOMAIN] = FakeClimateComponent(fake_vtherm)

    with patch("custom_components.vtherm_climate_replication.climate_replication.PluginClimate") as plugin_climate_cls:
        plugin = plugin_climate_cls.return_value
        plugin.linked_vtherm = None
        plugin.remove_listeners = MagicMock()
        plugin.call_linked_vtherm_action = AsyncMock()

        def _link_to_vtherm(vtherm) -> None:
            plugin.linked_vtherm = vtherm

        plugin.link_to_vtherm.side_effect = _link_to_vtherm

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

        plugin.link_to_vtherm.assert_called_once_with(fake_vtherm)

        hass.states.async_set(
            "climate.physical",
            HVACMode.HEAT,
            {
                ATTR_HVAC_MODE: HVACMode.HEAT,
                ATTR_PRESET_MODE: "eco",
                ATTR_TEMPERATURE: 19.0,
            },
        )
        await hass.async_block_till_done()
        plugin.call_linked_vtherm_action.reset_mock()

        hass.states.async_set(
            "climate.physical",
            HVACMode.COOL,
            {
                ATTR_HVAC_MODE: HVACMode.COOL,
                ATTR_PRESET_MODE: "boost",
                ATTR_TEMPERATURE: 21.5,
            },
        )
        await hass.async_block_till_done()

        assert plugin.call_linked_vtherm_action.await_args_list == [
            call(SERVICE_SET_HVAC_MODE, {ATTR_HVAC_MODE: HVACMode.COOL}),
            call(SERVICE_SET_PRESET_MODE, {ATTR_PRESET_MODE: "boost"}),
        ]


async def test_preset_temperature_change_is_ignored_but_manual_temperature_is_replicated(hass) -> None:
    """A temperature change caused by a preset should not be replicated twice."""
    fake_vtherm = FakeVtherm("climate.vtherm")
    hass.data[CLIMATE_DOMAIN] = FakeClimateComponent(fake_vtherm)

    with patch("custom_components.vtherm_climate_replication.climate_replication.PluginClimate") as plugin_climate_cls:
        plugin = plugin_climate_cls.return_value
        plugin.linked_vtherm = None
        plugin.remove_listeners = MagicMock()
        plugin.call_linked_vtherm_action = AsyncMock()

        def _link_to_vtherm(vtherm) -> None:
            plugin.linked_vtherm = vtherm

        plugin.link_to_vtherm.side_effect = _link_to_vtherm

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

        hass.states.async_set(
            "climate.physical",
            HVACMode.HEAT,
            {
                ATTR_HVAC_MODE: HVACMode.HEAT,
                ATTR_PRESET_MODE: "eco",
                ATTR_TEMPERATURE: 19.0,
            },
        )
        await hass.async_block_till_done()
        plugin.call_linked_vtherm_action.reset_mock()

        hass.states.async_set(
            "climate.physical",
            HVACMode.HEAT,
            {
                ATTR_HVAC_MODE: HVACMode.HEAT,
                ATTR_PRESET_MODE: "boost",
                ATTR_TEMPERATURE: 21.5,
            },
        )
        await hass.async_block_till_done()

        assert plugin.call_linked_vtherm_action.await_args_list == [
            call(SERVICE_SET_PRESET_MODE, {ATTR_PRESET_MODE: "boost"}),
        ]

        plugin.call_linked_vtherm_action.reset_mock()

        hass.states.async_set(
            "climate.physical",
            HVACMode.HEAT,
            {
                ATTR_HVAC_MODE: HVACMode.HEAT,
                ATTR_PRESET_MODE: "boost",
                ATTR_TEMPERATURE: 22.0,
            },
        )
        await hass.async_block_till_done()

        assert plugin.call_linked_vtherm_action.await_args_list == [
            call(SERVICE_SET_TEMPERATURE, {ATTR_TEMPERATURE: 22.0}),
        ]


async def test_switch_off_disables_replication(hass) -> None:
    """Replication should stop when the integration switch is off."""
    fake_vtherm = FakeVtherm("climate.vtherm")
    hass.data[CLIMATE_DOMAIN] = FakeClimateComponent(fake_vtherm)

    with patch("custom_components.vtherm_climate_replication.climate_replication.PluginClimate") as plugin_climate_cls:
        plugin = plugin_climate_cls.return_value
        plugin.linked_vtherm = None
        plugin.remove_listeners = MagicMock()
        plugin.call_linked_vtherm_action = AsyncMock()

        def _link_to_vtherm(vtherm) -> None:
            plugin.linked_vtherm = vtherm

        plugin.link_to_vtherm.side_effect = _link_to_vtherm

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

        await hass.services.async_call(
            "switch",
            "turn_off",
            {ATTR_ENTITY_ID: "switch.physical_vtherm_replication"},
            blocking=True,
        )
        await hass.async_block_till_done()

        hass.states.async_set(
            "climate.physical",
            HVACMode.HEAT,
            {
                ATTR_HVAC_MODE: HVACMode.HEAT,
                ATTR_PRESET_MODE: "eco",
                ATTR_TEMPERATURE: 19.0,
            },
        )
        await hass.async_block_till_done()

        hass.states.async_set(
            "climate.physical",
            HVACMode.COOL,
            {
                ATTR_HVAC_MODE: HVACMode.COOL,
                ATTR_PRESET_MODE: "boost",
                ATTR_TEMPERATURE: 21.5,
            },
        )
        await hass.async_block_till_done()

        plugin.call_linked_vtherm_action.assert_not_called()


async def test_preset_not_replicated_when_vtherm_does_not_support_it(hass) -> None:
    """Preset replication should be skipped when the VTherm does not support preset mode."""
    fake_vtherm = FakeVtherm("climate.vtherm", supported_features=0)
    hass.data[CLIMATE_DOMAIN] = FakeClimateComponent(fake_vtherm)

    with patch("custom_components.vtherm_climate_replication.climate_replication.PluginClimate") as plugin_climate_cls:
        plugin = plugin_climate_cls.return_value
        plugin.linked_vtherm = None
        plugin.remove_listeners = MagicMock()
        plugin.call_linked_vtherm_action = AsyncMock()

        def _link_to_vtherm(vtherm) -> None:
            plugin.linked_vtherm = vtherm

        plugin.link_to_vtherm.side_effect = _link_to_vtherm

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

        hass.states.async_set(
            "climate.physical",
            HVACMode.HEAT,
            {
                ATTR_HVAC_MODE: HVACMode.HEAT,
                ATTR_PRESET_MODE: "eco",
                ATTR_TEMPERATURE: 19.0,
            },
        )
        await hass.async_block_till_done()
        plugin.call_linked_vtherm_action.reset_mock()

        hass.states.async_set(
            "climate.physical",
            HVACMode.HEAT,
            {
                ATTR_HVAC_MODE: HVACMode.HEAT,
                ATTR_PRESET_MODE: "boost",
                ATTR_TEMPERATURE: 19.0,
            },
        )
        await hass.async_block_till_done()

        called_services = [c.args[0] for c in plugin.call_linked_vtherm_action.await_args_list]
        assert SERVICE_SET_PRESET_MODE not in called_services
