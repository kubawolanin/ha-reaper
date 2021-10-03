"""Reaper media_player entity."""
import json
import logging
from typing import Any, Dict

import voluptuous as vol

from homeassistant.components.media_player import MediaPlayerEntity
from homeassistant.components.media_player.const import (
    MEDIA_TYPE_MUSIC,
    SUPPORT_NEXT_TRACK,
    SUPPORT_PLAY,
    SUPPORT_PREVIOUS_TRACK,
    SUPPORT_STOP,
    SUPPORT_VOLUME_SET,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_IDLE, STATE_OFF, STATE_PAUSED, STATE_PLAYING
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv, entity_platform
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import ReaperDataUpdateCoordinator
from .const import ATTR_ID, DOMAIN, SERVICE_RECORD, SERVICE_RUN_ACTION

SUPPORT_REAPER = (
    SUPPORT_PLAY
    | SUPPORT_VOLUME_SET
    # | SUPPORT_PAUSE
    | SUPPORT_PREVIOUS_TRACK
    | SUPPORT_NEXT_TRACK
    | SUPPORT_STOP
)


_LOGGER = logging.getLogger(__name__)


PLAYBACK_DICT = {
    "stopped": STATE_IDLE,
    "playing": STATE_PLAYING,
    "paused": STATE_PAUSED,
    "recording": STATE_PLAYING,
    "recordpaused": STATE_PAUSED,
}


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the Reaper media player."""
    coordinator: ReaperDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    platform = entity_platform.current_platform.get()

    platform.async_register_entity_service(
        SERVICE_RECORD,
        {},
        "async_reaper_record",
    )

    platform.async_register_entity_service(
        SERVICE_RUN_ACTION,
        {
            vol.Required(ATTR_ID): cv.string,
        },
        "async_reaper_run_action",
    )

    async_add_entities([ReaperMediaPlayer(coordinator)], False)


class ReaperMediaPlayer(CoordinatorEntity, MediaPlayerEntity):
    """Representation of a Reaper media player."""

    coordinator: ReaperDataUpdateCoordinator

    def __init__(self, coordinator: ReaperDataUpdateCoordinator):
        """Initialize a Reaper media player."""
        super().__init__(coordinator)
        self._name = f"{coordinator.hostname} Reaper Transport"

        self.coordinator = coordinator
        self._unique_id = f"{coordinator.hostname}-mediaplayer"
        self.status = json.loads(coordinator.data)
        self._state = STATE_OFF

    async def async_update(self) -> None:
        """Update Reaper entity."""
        await self.coordinator.async_request_refresh()
        self._state = PLAYBACK_DICT[json.loads(self.coordinator.data).get("play_state")]
        self.status = json.loads(self.coordinator.data)

    @property
    def should_poll(self) -> bool:
        return True

    @property
    def name(self) -> str:
        """Return the name of the media player."""
        return self._name

    @property
    def state(self) -> StateType:
        """Return the state of the device."""
        return self._state

    @property
    def media_content_type(self) -> Any:
        """Content type of current playing media."""
        return MEDIA_TYPE_MUSIC

    @property
    def supported_features(self) -> Any:
        """Return the supported features."""
        return SUPPORT_REAPER

    @property
    def device_info(self) -> Dict[str, Any]:
        """Return the device info."""
        return {
            "identifiers": {(DOMAIN, self.coordinator.hostname)},
            "name": self.coordinator.hostname,
            "manufacturer": "Cockos Reaper",
        }

    @property
    def unique_id(self) -> str:
        """Return the unique id."""
        return self._unique_id

    async def async_turn_on(self) -> None:
        """Turn on."""
        await self.coordinator.async_refresh()

    async def async_turn_off(self) -> None:
        """Turn off."""
        await self.coordinator.async_refresh()

    async def async_media_play(self) -> None:
        """Play."""
        await self.coordinator.reaperdaw.play()
        await self.coordinator.async_refresh()

    async def async_media_pause(self) -> None:
        """Play."""
        await self.coordinator.reaperdaw.pause()
        await self.coordinator.async_refresh()

    async def async_media_stop(self) -> None:
        """Send stop command to media player."""
        await self.coordinator.reaperdaw.stop()
        await self.coordinator.async_refresh()

    async def async_media_next_track(self) -> None:
        """Send next track command."""
        await self.coordinator.reaperdaw.fastForward()
        await self.coordinator.async_refresh()

    async def async_media_previous_track(self) -> None:
        """Send the previous track command."""
        await self.coordinator.reaperdaw.rewind()
        await self.coordinator.async_refresh()

    async def async_set_volume_level(self, volume: str) -> None:
        """Set volume level, range 0..1."""
        await self.async_reaper_set_volume_level(volume)

    async def async_reaper_record(self) -> None:
        """Record a piece of audio in Reaper."""
        await self.coordinator.reaperdaw.record()
        await self.coordinator.async_refresh()

    async def async_reaper_run_action(self, action_id: str) -> None:
        """Set reaper configuration actionId."""
        await self.coordinator.reaperdaw.sendCommand(action_id)
        await self.coordinator.async_refresh()

    async def async_reaper_set_volume_level(self, volume_level: str) -> None:
        """Set volume level for a stream, range 0..1."""
        await self.coordinator.reaperdaw.setMasterVolume(int(volume_level))

    async def async_added_to_hass(self) -> None:
        """Connect to dispatcher listening for entity data notifications."""
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )
