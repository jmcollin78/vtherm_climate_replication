"""Tests for the vtherm_climate_replication config flow."""

from __future__ import annotations

from homeassistant import config_entries, data_entry_flow

from custom_components.vtherm_climate_replication.const import (
    DATA_PHYSICAL_CLIMATE,
    DATA_TARGET_CLIMATE,
    DOMAIN,
)


async def test_user_flow_creates_entry(hass) -> None:
    """The user flow should create a config entry."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": config_entries.SOURCE_USER},
    )

    assert result["type"] is data_entry_flow.FlowResultType.FORM
    assert result["step_id"] == "user"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            DATA_PHYSICAL_CLIMATE: "climate.physical",
            DATA_TARGET_CLIMATE: "climate.vtherm",
        },
    )

    assert result["type"] is data_entry_flow.FlowResultType.CREATE_ENTRY
    assert result["title"] == "climate.physical -> climate.vtherm"
    assert result["data"] == {
        DATA_PHYSICAL_CLIMATE: "climate.physical",
        DATA_TARGET_CLIMATE: "climate.vtherm",
    }


async def test_user_flow_rejects_same_climate(hass) -> None:
    """The user flow should reject identical climate entities."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": config_entries.SOURCE_USER},
    )

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            DATA_PHYSICAL_CLIMATE: "climate.same",
            DATA_TARGET_CLIMATE: "climate.same",
        },
    )

    assert result["type"] is data_entry_flow.FlowResultType.FORM
    assert result["errors"] == {"base": "same_climate"}
