"""The Bulgarian Utility Outage Checker integration."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv
import voluptuous as vol

from .const import DOMAIN
from .coordinator import BulgarianUtilityOutageCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.BINARY_SENSOR]

SERVICE_CHECK_NOW = "check_now"

SERVICE_CHECK_NOW_SCHEMA = vol.Schema(
    {
        vol.Required("entity_id"): cv.entity_ids,
    }
)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Bulgarian Utility Outage Checker from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    # Register www folder for static files (Lovelace card)
    hass.http.register_static_path(
        f"/local/community/{DOMAIN}",
        hass.config.path(f"custom_components/{DOMAIN}/www"),
        cache_headers=False,
    )

    coordinator = BulgarianUtilityOutageCoordinator(hass, entry)
    
    # Perform first refresh
    _LOGGER.info("Performing first refresh for %s", entry.data.get("identifier"))
    await coordinator.async_config_entry_first_refresh()
    _LOGGER.info(
        "First refresh complete for %s. Next update in %d minutes",
        entry.data.get("identifier"),
        coordinator.check_interval,
    )

    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register update listener for options changes
    entry.async_on_unload(entry.add_update_listener(update_listener))

    async def async_check_now(call: ServiceCall) -> None:  # noqa: ARG001
        """Handle the check_now service call."""
        await coordinator.async_request_refresh()

    # Register service
    hass.services.async_register(
        DOMAIN,
        SERVICE_CHECK_NOW,
        async_check_now,
        schema=SERVICE_CHECK_NOW_SCHEMA,
    )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    _LOGGER.info(
        "Options updated for %s, reloading entry to apply new settings",
        entry.data.get("identifier"),
    )
    await hass.config_entries.async_reload(entry.entry_id)
