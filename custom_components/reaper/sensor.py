"""Support for the Reaper service."""
from __future__ import annotations

import json
import logging
from typing import Any, cast
from operator import attrgetter, itemgetter

from homeassistant.components.sensor import (
    DOMAIN as PLATFORM,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_ATTRIBUTION
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import entity_registry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import ReaperDataUpdateCoordinator
from .const import (
    ATTRIBUTION,
    DOMAIN,
    SENSORS,
)

PARALLEL_UPDATES = 1

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Add a Reaper entities from a config_entry."""
    coordinator: ReaperDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    sensors: list[ReaperSensor] = []
    for description in SENSORS:
        sensors.append(ReaperSensor(coordinator, description))

    async_add_entities(sensors)


class ReaperSensor(CoordinatorEntity, SensorEntity):
    """Define an Reaper sensor."""

    coordinator: ReaperDataUpdateCoordinator

    def __init__(
        self,
        coordinator: ReaperDataUpdateCoordinator,
        description: SensorEntityDescription,
    ) -> None:
        """Initialize."""
        super().__init__(coordinator)

        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.hostname)},
            "name": coordinator.hostname,
            "manufacturer": "Cockos Reaper",
            "entry_type": "service",
        }
        self._attr_unique_id = f"{coordinator.hostname}-{description.key}"
        self._attrs = {ATTR_ATTRIBUTION: ATTRIBUTION}
        _LOGGER.debug("Received data: %s", coordinator.data)
        _LOGGER.debug("Type: %s", type(coordinator.data))
        status = coordinator.data
        self._sensor_data = status.get(description.key)
        self.entity_description = description

    @property
    def native_value(self) -> StateType:
        """Return the state."""
        return cast(StateType, self._sensor_data)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""

        return self._attrs

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._sensor_data = getattr(self.coordinator.data, self.entity_description.key)
        self.async_write_ha_state()
