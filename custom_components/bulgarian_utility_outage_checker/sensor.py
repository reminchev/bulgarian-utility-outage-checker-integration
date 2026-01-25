"""Sensor platform for Bulgarian Utility Outage Checker."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    ATTR_DETAILS,
    ATTR_HAS_OUTAGE,
    ATTR_IDENTIFIER,
    ATTR_LAST_CHECK,
    ATTR_OUTAGE_TYPE,
    ATTR_TIMESTAMP,
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
    """Set up the sensor platform."""
    coordinator: BulgarianUtilityOutageCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        [
            UtilityOutageStatusSensor(coordinator, entry),
        ],
        True,
    )


class UtilityOutageStatusSensor(
    CoordinatorEntity[BulgarianUtilityOutageCoordinator], SensorEntity
):
    """Sensor for utility outage status."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:transmission-tower"

    def __init__(
        self,
        coordinator: BulgarianUtilityOutageCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._identifier = entry.data[CONF_IDENTIFIER]
        self._attr_unique_id = f"{entry.entry_id}_status"
        self._attr_name = "Status"
        
        # Device info for grouping entities
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=f"Bulgarian Utility Outage Checker - {self._identifier}",
            manufacturer="ERM West",
            model="Outage Checker",
        )

    @property
    def native_value(self) -> str:
        """Return the state of the sensor."""
        if self.coordinator.data:
            if self.coordinator.data.get("has_outage"):
                return self.coordinator.data.get("outage_type", "Unknown")
            return "Няма аварии"
        return "Unknown"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        if not self.coordinator.data:
            return {}

        return {
            ATTR_IDENTIFIER: self.coordinator.data.get("identifier"),
            ATTR_HAS_OUTAGE: self.coordinator.data.get("has_outage", False),
            ATTR_OUTAGE_TYPE: self.coordinator.data.get("outage_type", OUTAGE_TYPE_NONE),
            ATTR_DETAILS: self.coordinator.data.get("details", []),
            ATTR_LAST_CHECK: self.coordinator.data.get("last_check"),
            ATTR_TIMESTAMP: self.coordinator.data.get("timestamp"),
        }

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self.coordinator.last_update_success
