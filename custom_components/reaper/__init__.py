"""The Reaper component."""
from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any, Final

from aiohttp import ClientSession
from aiohttp.client_exceptions import ClientConnectorError
import async_timeout
from reaperdaw import Reaper, ReaperError

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    CONF_HOSTNAME,
    CONF_PASSWORD,
    CONF_PORT,
    CONF_UPDATE_INTERVAL,
    CONF_USERNAME,
    DEFAULT_PORT,
    DEFAULT_UPDATE_INTERVAL,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS: Final[list[str]] = ["sensor", "switch", "media_player"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Reaper as config entry."""
    hostname = entry.data[CONF_HOSTNAME]
    port = entry.data[CONF_PORT]
    username = entry.data[CONF_USERNAME]
    password = entry.data[CONF_PASSWORD]
    update_interval = entry.data[CONF_UPDATE_INTERVAL]
    websession = async_get_clientsession(hass)

    coordinator = ReaperDataUpdateCoordinator(
        hass,
        websession,
        hostname,
        port,
        username,
        password,
        update_interval,
    )
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    for component in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, component)
        )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok: bool = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


class ReaperDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Reaper data API."""

    def __init__(  # pylint: disable=R0913
        self,
        hass: HomeAssistant,
        session: ClientSession,
        hostname: str,
        port: int = DEFAULT_PORT,
        username: str = "",
        password: str = "",
        update_interval: int = DEFAULT_UPDATE_INTERVAL,
    ) -> None:
        """Initialize."""
        self.hostname = hostname
        self.port = port
        self.update_interval = timedelta(seconds=update_interval)
        self.reaperdaw = Reaper(session, hostname, port, username, password)

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=update_interval),
        )

    async def _async_update_data(self) -> str | Any:
        """Update data via library."""
        try:
            with async_timeout.timeout(10):
                status = await self.reaperdaw.getStatus()
                return status
        except (ReaperError, ClientConnectorError) as error:
            raise UpdateFailed(error) from error
