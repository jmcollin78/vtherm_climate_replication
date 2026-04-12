"""Config flow for the vtherm_climate_replication integration."""

from __future__ import annotations

from typing import Any, Self

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.components.climate import DOMAIN as CLIMATE_DOMAIN
from homeassistant.helpers import selector

from .const import DATA_PHYSICAL_CLIMATE, DATA_TARGET_CLIMATE, DOMAIN


def _build_schema() -> vol.Schema:
    """Build the user step schema."""
    climate_selector = selector.EntitySelector(
        selector.EntitySelectorConfig(domain=CLIMATE_DOMAIN)
    )
    return vol.Schema(
        {
            vol.Required(DATA_PHYSICAL_CLIMATE): climate_selector,
            vol.Required(DATA_TARGET_CLIMATE): climate_selector,
        }
    )


class VthermClimateReplicationConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for vtherm_climate_replication."""

    VERSION = 1

    def is_matching(self, other_flow: Self) -> bool:
        """Return whether another flow matches this flow."""
        return False

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            if user_input[DATA_PHYSICAL_CLIMATE] == user_input[DATA_TARGET_CLIMATE]:
                errors["base"] = "same_climate"
            elif any(
                entry.data.get(DATA_PHYSICAL_CLIMATE) == user_input[DATA_PHYSICAL_CLIMATE]
                and entry.data.get(DATA_TARGET_CLIMATE) == user_input[DATA_TARGET_CLIMATE]
                for entry in self._async_current_entries()
            ):
                return self.async_abort(reason="already_configured")
            else:
                return self.async_create_entry(
                    title=(
                        f"{user_input[DATA_PHYSICAL_CLIMATE]} -> "
                        f"{user_input[DATA_TARGET_CLIMATE]}"
                    ),
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=_build_schema(),
            errors=errors,
        )