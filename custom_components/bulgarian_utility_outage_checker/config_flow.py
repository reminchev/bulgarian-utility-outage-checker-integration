"""Config flow for Bulgarian Utility Outage Checker integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import config_validation as cv

from .const import (
    CONF_CHECK_INTERVAL,
    CONF_IDENTIFIER,
    CONF_PROVIDER,
    DEFAULT_CHECK_INTERVAL,
    DOMAIN,
    PROVIDER_ENERGOHOLD,
    PROVIDERS,
)

_LOGGER = logging.getLogger(__name__)

STEP_PROVIDER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_PROVIDER, default=PROVIDER_ENERGOHOLD): vol.In(PROVIDERS),
    }
)

STEP_IDENTIFIER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_IDENTIFIER): cv.string,
        vol.Optional(CONF_CHECK_INTERVAL, default=DEFAULT_CHECK_INTERVAL): vol.All(
            vol.Coerce(int), vol.Range(min=1, max=1440)
        ),
    }
)


class ConfigFlow(config_entries.ConfigFlow):
    """Handle a config flow for Bulgarian Utility Outage Checker."""

    VERSION = 1
    DOMAIN = DOMAIN

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._provider: str = PROVIDER_ENERGOHOLD

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the provider selection step."""
        if user_input is not None:
            self._provider = user_input[CONF_PROVIDER]
            return await self.async_step_identifier()

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_PROVIDER_DATA_SCHEMA,
        )

    async def async_step_identifier(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the identifier input step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Combine provider and identifier data
            identifier = user_input[CONF_IDENTIFIER]
            full_data = {
                CONF_PROVIDER: self._provider,
                CONF_IDENTIFIER: identifier,
                CONF_CHECK_INTERVAL: user_input.get(
                    CONF_CHECK_INTERVAL, DEFAULT_CHECK_INTERVAL
                ),
            }

            # Create unique ID from provider and identifier
            await self.async_set_unique_id(
                f"bulgarian_outage_{self._provider}_{identifier}"
            )
            self._abort_if_unique_id_configured()

            provider_name = PROVIDERS[self._provider]
            return self.async_create_entry(
                title=f"{provider_name} - {identifier}",
                data=full_data,
            )

        return self.async_show_form(
            step_id="identifier",
            data_schema=STEP_IDENTIFIER_DATA_SCHEMA,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Create the options flow."""
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for Bulgarian Utility Outage Checker."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_CHECK_INTERVAL,
                        default=self.config_entry.options.get(
                            CONF_CHECK_INTERVAL,
                            self.config_entry.data.get(
                                CONF_CHECK_INTERVAL, DEFAULT_CHECK_INTERVAL
                            ),
                        ),
                    ): vol.All(vol.Coerce(int), vol.Range(min=1, max=1440)),
                }
            ),
        )
