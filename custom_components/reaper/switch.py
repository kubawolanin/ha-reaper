"""Reaper switch."""
import json
import logging
from typing import Any, Dict

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import ReaperDataUpdateCoordinator
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the Reaper switch."""
    coordinator: ReaperDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities([ReaperRecordingSwitch(hass, coordinator)], False)
    async_add_entities([ReaperMetronomeSwitch(hass, coordinator)], False)
    async_add_entities([ReaperRepeatSwitch(hass, coordinator)], False)


class ReaperSwitch(CoordinatorEntity, SwitchEntity):
    """Representation of a generic Reaper switch entity."""

    coordinator: ReaperDataUpdateCoordinator

    def __init__(
        self, hass: HomeAssistant, coordinator: ReaperDataUpdateCoordinator
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)

        self.coordinator = coordinator
        self.status = json.loads(coordinator.data)
        self.hass = hass
        self._name = ""
        self._unique_id = ""
        self._icon = ""

    @property
    def name(self) -> str:
        """Return the name of the switch."""
        return self._name

    @property
    def icon(self) -> str:
        """Return the icon of the switch."""
        return self._icon

    @property
    def device_info(self) -> Dict[str, Any]:
        """Return the device info."""
        return {
            "identifiers": {(DOMAIN, self.coordinator.hostname)},
            "name": self.coordinator.hostname,
            "manufacturer": "Cockos Reaper",
            "configuration_url": f"http://{self.coordinator.hostname}:{self.coordinator.port}",
        }

    @property
    def unique_id(self) -> str:
        """Return the unique id."""
        return self._unique_id

    async def async_added_to_hass(self) -> None:
        """Connect to dispatcher listening for entity data notifications."""
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )

    async def async_update(self) -> None:
        """Update Reaper entity."""
        await self.coordinator.async_request_refresh()
        self.status = json.loads(self.coordinator.data)


class ReaperRecordingSwitch(ReaperSwitch):
    """Representation of a Reaper recording switch."""

    def __init__(
        self, hass: HomeAssistant, coordinator: ReaperDataUpdateCoordinator
    ) -> None:
        """Initialize the recording switch."""
        super().__init__(hass, coordinator)
        self._name = "Recording"
        self._unique_id = f"{coordinator.hostname}-recording"
        self._icon = "mdi:circle"

    @property
    def is_on(self) -> Any:
        """Return if switch is on."""
        if self.coordinator.data:
            return json.loads(self.coordinator.data).get("play_state") == "recording"
        return None

    async def async_turn_on(self) -> None:
        """Turn on the recording."""
        await self.coordinator.reaperdaw.record()
        await self.coordinator.async_refresh()

    async def async_turn_off(self) -> None:
        """Turn off the recording."""
        await self.coordinator.reaperdaw.stop()
        await self.coordinator.async_refresh()


class ReaperMetronomeSwitch(ReaperSwitch):
    """Representation of a Reaper metronome switch."""

    def __init__(
        self, hass: HomeAssistant, coordinator: ReaperDataUpdateCoordinator
    ) -> None:
        """Initialize the metronome switch."""
        super().__init__(hass, coordinator)
        self._name = "Metronome"
        self._unique_id = f"{coordinator.hostname}-metronome"
        self._icon = "mdi:metronome"

    @property
    def is_on(self) -> Any:
        """Return if metronome is on."""
        if self.coordinator.data is not None:
            return json.loads(self.coordinator.data).get("metronome")
        return None

    async def async_turn_on(self) -> None:
        """Turn on metronome."""
        await self.coordinator.reaperdaw.enableMetronome()
        await self.coordinator.async_refresh()

    async def async_turn_off(self) -> None:
        """Turn off metronome."""
        await self.coordinator.reaperdaw.disableMetronome()
        await self.coordinator.async_refresh()


class ReaperRepeatSwitch(ReaperSwitch):
    """Representation of a Reaper repeat switch."""

    def __init__(
        self, hass: HomeAssistant, coordinator: ReaperDataUpdateCoordinator
    ) -> None:
        """Intialize the repeat switch."""
        super().__init__(hass, coordinator)
        self._name = "Repeat"
        self._unique_id = f"{coordinator.hostname}-repeat"
        self._icon = "mdi:repeat"

    @property
    def is_on(self) -> Any:
        """Return if repeat is on."""
        if self.coordinator.data is not None:
            return json.loads(self.coordinator.data).get("transport").get("repeat")
        return None

    async def async_turn_on(self) -> None:
        """Turn on repeat."""
        await self.coordinator.reaperdaw.enableRepeat()
        await self.coordinator.async_refresh()

    async def async_turn_off(self) -> None:
        """Turn off repeat."""
        await self.coordinator.reaperdaw.disableRepeat()
        await self.coordinator.async_refresh()
