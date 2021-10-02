"""Provide info to system health."""
from __future__ import annotations

from homeassistant.components import system_health
from homeassistant.core import HomeAssistant, callback

from .const import (
    DOMAIN,
)


@callback
def async_register(  # pylint:disable=unused-argument
    hass: HomeAssistant,
    register: system_health.SystemHealthRegistration,
) -> None:
    """Register system health callbacks."""
    register.async_register_info(system_health_info)


async def system_health_info(hass: HomeAssistant, config_entry) -> dict[str, str]:
    """Get info for the info page."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    hostname = coordinator.hostname
    port = coordinator.port
    return {
        "can_reach_server": system_health.async_check_can_reach_url(
            hass, f"http://{hostname}:{port}"
        )
    }
