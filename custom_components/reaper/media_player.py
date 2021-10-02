"""Reaper media_player entity."""
import json
import logging

import voluptuous as vol
from homeassistant.components.media_player.const import (
    ATTR_MEDIA_VOLUME_LEVEL,
    MEDIA_TYPE_MUSIC,
    SUPPORT_PLAY,
    SUPPORT_PAUSE,
    SUPPORT_PREVIOUS_TRACK,
    SUPPORT_NEXT_TRACK,
    SUPPORT_STOP,
    SUPPORT_VOLUME_SET,
)
from homeassistant.components.media_player import (
    MediaPlayerEntity,
    SERVICE_VOLUME_SET,
)
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import entity_platform
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import ReaperDataUpdateCoordinator
from .const import (
    ATTR_ID,
    DOMAIN,
    SERVICE_PLAY,
    SERVICE_STOP,
    SERVICE_PAUSE,
    SERVICE_REWIND,
    SERVICE_FAST_FORWARD,
    SERVICE_RECORD,
    SERVICE_RUN_ACTION,
)

SUPPORT_REAPER = (
    SUPPORT_PLAY
    | SUPPORT_VOLUME_SET
    | SUPPORT_PAUSE
    | SUPPORT_PREVIOUS_TRACK
    | SUPPORT_NEXT_TRACK
    | SUPPORT_STOP
)


_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Reaper media player."""
    coordinator: ReaperDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    platform = entity_platform.current_platform.get()

    platform.async_register_entity_service(
        SERVICE_PLAY,
        {},
        "async_reaper_play",
    )

    platform.async_register_entity_service(
        SERVICE_STOP,
        {},
        "async_reaper_stop",
    )

    platform.async_register_entity_service(
        SERVICE_PAUSE,
        {},
        "async_reaper_pause",
    )

    platform.async_register_entity_service(
        SERVICE_REWIND,
        {},
        "async_reaper_rewind",
    )

    platform.async_register_entity_service(
        SERVICE_FAST_FORWARD,
        {},
        "async_reaper_fast_forward",
    )

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

    platform.async_register_entity_service(
        SERVICE_VOLUME_SET,
        {
            vol.Required(ATTR_MEDIA_VOLUME_LEVEL): cv.small_float,
        },
        "async_reaper_set_volume_level",
    )

    async_add_entities([ReaperMediaPlayer(coordinator)], False)


class ReaperMediaPlayer(MediaPlayerEntity, CoordinatorEntity):
    """Representation of a Reaper media player."""

    coordinator: ReaperDataUpdateCoordinator

    def __init__(self, coordinator: ReaperDataUpdateCoordinator):
        """Initialize a Reaper media player."""
        super().__init__(coordinator)
        self._name = "Reaper Transport"
        self.coordinator = coordinator
        self._unique_id = f"{coordinator.hostname}-mediaplayer"
        self.status = json.loads(self.coordinator.data)
        self._is_on = self.status.get("play_state")
        self._play_state = self.status.get("play_state")

    # def update(self):
    #     """Update the States"""
    #     if self._play_state:
    #         if self._play_state == "playing":
    #             self._state = STATE_PLAYING
    #         else:
    #             self._state = STATE_PAUSED

    @property
    def should_poll(self):
        return False

    @property
    def name(self):
        """Return the name of the media player."""
        return self._name

    @property
    def media_content_type(self):
        """Content type of current playing media."""
        return MEDIA_TYPE_MUSIC

    @property
    def is_on(self):
        """Return True if device is on."""
        return self._is_on

    @property
    def supported_features(self):
        """Return the supported features."""
        return SUPPORT_REAPER

    @property
    def device_info(self):
        """Return the device info."""
        return {
            "identifiers": {(DOMAIN, self.coordinator.hostname)},
            "name": self.coordinator.hostname,
            "manufacturer": "Cockos Reaper",
        }

    @property
    def unique_id(self):
        """Return the unique id."""
        return self._unique_id

    async def async_turn_on(self):
        """Turn on."""
        await self.coordinator.async_refresh()

    async def async_turn_off(self):
        """Turn off."""
        await self.coordinator.async_refresh()

    async def async_play_media(self, **kwargs):
        """Play."""
        await self.coordinator.reaperdaw.play()
        await self.coordinator.async_refresh()

    async def async_media_stop(self):
        """Send stop command to media player."""
        await self.coordinator.reaperdaw.stop()
        await self.coordinator.async_refresh()

    async def async_media_next_track(self):
        """Send next track command."""
        await self.coordinator.reaperdaw.fastForward()
        await self.coordinator.async_refresh()

    async def async_media_previous_track(self):
        """Send the previous track command."""
        await self.coordinator.reaperdaw.rewind()
        await self.coordinator.async_refresh()

    async def async_set_volume_level(self, volume):
        """Set volume level, range 0..1."""
        await self.async_reaper_set_volume_level(volume)

    async def async_reaper_play(self):
        """Play a piece of audio in Reaper."""
        await self.coordinator.reaperdaw.play()
        await self.coordinator.async_refresh()

    async def async_reaper_stop(self):
        """Stop a piece of audio in Reaper."""
        await self.coordinator.reaperdaw.stop()
        await self.coordinator.async_refresh()

    async def async_reaper_pause(self):
        """Pause a piece of audio in Reaper."""
        await self.coordinator.reaperdaw.pause()
        await self.coordinator.async_refresh()

    async def async_reaper_rewind(self):
        """Rewind a piece of audio in Reaper."""
        await self.coordinator.reaperdaw.rewind()
        await self.coordinator.async_refresh()

    async def async_reaper_fast_forward(self):
        """Fast_forward a piece of audio in Reaper."""
        await self.coordinator.reaperdaw.fastForward()
        await self.coordinator.async_refresh()

    async def async_reaper_record(self):
        """Record a piece of audio in Reaper."""
        await self.coordinator.reaperdaw.record()
        await self.coordinator.async_refresh()

    async def async_reaper_run_action(self, id):
        """Set reaper configuration actionId."""
        await self.coordinator.reaperdaw.sendCommand(id)
        await self.coordinator.async_refresh()

    async def async_reaper_set_volume_level(self, volume_level):
        """Set volume level for a stream, range 0..1."""
        await self.coordinator.reaperdaw.setMasterVolume(int(volume_level))

    async def async_added_to_hass(self):
        """Connect to dispatcher listening for entity data notifications."""
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )

    async def async_update(self):
        """Update Reaper entity."""
        await self.coordinator.async_request_refresh()
