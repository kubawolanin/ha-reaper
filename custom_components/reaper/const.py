"""Constants for Reaper integration."""
from __future__ import annotations
from typing import Final
from homeassistant.components.sensor import SensorEntityDescription

ATTRIBUTION: Final = (
    "Data provided by Cockos Inc REAPER web interface."
)

ATTR_LEVEL: Final = "level"
ATTR_TREND: Final = "trend"
ATTR_VALUE: Final = "value"

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
# mdi:play-circle-outline play_state
# mdi:timeline-clock-outline time_signature
# mdi:metronome-tick tempo?

SENSORS: Final[tuple[SensorEntityDescription, ...]] = (
    # SensorEntityDescription(
    #     key="transport.playstate",
    #     device_class="reaper__playstate",
    #     icon="mdi:play-circle-outline",
    #     name="Play State",
    # ),
    SensorEntityDescription(
        key="number_of_tracks",
        device_class="reaper__number_of_tracks",
        icon="mdi:audio-input-stereo-minijack",
        name="Number of tracks",
    ),
)
