"""Constants for Reaper integration."""
from __future__ import annotations
from typing import Final
from homeassistant.components.sensor import SensorEntityDescription

ATTRIBUTION: Final = (
    "Data provided by Cockos Inc REAPER web interface."
)

CONF_HOSTNAME: Final = "hostname"
CONF_PORT: Final = "port"
CONF_USERNAME: Final = "username"
CONF_PASSWORD: Final = "password"
CONF_UPDATE_INTERVAL = "update_interval"

DEFAULT_PORT = 8080
DEFAULT_UPDATE_INTERVAL = 30
DOMAIN: Final = "reaper"

# mdi:metronome
# mdi:repeat-variant
# mdi:volume-mute
# mdi:waveform

SENSORS: Final[tuple[SensorEntityDescription, ...]] = (
    SensorEntityDescription(
        key="play_state",
        device_class="reaper__play_state",
        icon="mdi:play-circle-outline",
        name="Play state",
    ),
    SensorEntityDescription(
        key="number_of_tracks",
        device_class="reaper__number_of_tracks",
        icon="mdi:audio-input-stereo-minijack",
        name="Number of tracks",
    ),
    SensorEntityDescription(
        key="time_signature",
        device_class="reaper__time_signature",
        icon="mdi:timeline-clock-outline",
        name="Time signature",
    ),
)
