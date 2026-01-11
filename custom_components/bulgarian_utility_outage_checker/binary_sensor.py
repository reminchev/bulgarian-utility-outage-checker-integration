"""Binary sensor platform for Bulgarian Utility Outage Checker."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    ATTR_DETAILS,
    ATTR_LAST_CHECK,
    ATTR_OUTAGE_TYPE,
    CONF_IDENTIFIER,
    DOMAIN,
    OUTAGE_TYPE_NONE,
)
from .coordinator import BulgarianUtilityOutageCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the binary sensor platform."""
    coordinator: BulgarianUtilityOutageCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        [
            UtilityOutageBinarySensor(coordinator, entry),
        ],
        True,
    )


class UtilityOutageBinarySensor(
    CoordinatorEntity[BulgarianUtilityOutageCoordinator], BinarySensorEntity
):
    """Binary sensor for utility outage detection."""

    _attr_has_entity_name = True
    _attr_device_class = BinarySensorDeviceClass.PROBLEM

    def __init__(
        self,
        coordinator: BulgarianUtilityOutageCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self._identifier = entry.data[CONF_IDENTIFIER]
        self._attr_unique_id = f"{entry.entry_id}_outage"
        self._attr_name = "Outage Detected"
        
        # Device info for grouping entities
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": f"Bulgarian Utility Outage Checker - {self._identifier}",
            "manufacturer": "ERM West",
            "model": "Outage Checker",
            "entry_type": "service",
        }

    @property
    def is_on(self) -> bool:
        """Return true if the binary sensor is on."""
        if self.coordinator.data:
            return self.coordinator.data.get("has_outage", False)
        return False

    @property
    def icon(self) -> str:
        """Return the icon to use in the frontend."""
        if self.is_on:
            return "mdi:power-plug-off"
        return "mdi:power-plug"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        if not self.coordinator.data:
            return {}

        return {
            ATTR_OUTAGE_TYPE: self.coordinator.data.get("outage_type", OUTAGE_TYPE_NONE),
            ATTR_LAST_CHECK: self.coordinator.data.get("last_check"),
            ATTR_DETAILS: self.coordinator.data.get("details", []),
        }

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self.coordinator.last_update_success
