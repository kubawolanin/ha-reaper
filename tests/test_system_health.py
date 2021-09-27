"""Test Reaper system health."""
import asyncio

from aiohttp import ClientError
from pytest_homeassistant_custom_component.common import get_system_health_info

from custom_components.reaper.const import DOMAIN
from homeassistant.setup import async_setup_component


async def test_reaper_system_health(hass, aioclient_mock):
    """Test Reaper system health."""
    aioclient_mock.get("http://localhost:8080", text="")
    hass.config.components.add(DOMAIN)
    assert await async_setup_component(hass, "system_health", {})

    info = await get_system_health_info(hass, DOMAIN)

    for key, val in info.items():
        if asyncio.iscoroutine(val):
            info[key] = await val

    assert info == {"can_reach_server": "ok"}


async def test_reaper_system_health_fail(hass, aioclient_mock):
    """Test Reaper system health."""
    aioclient_mock.get("http://localhost:8080", exc=ClientError)
    hass.config.components.add(DOMAIN)
    assert await async_setup_component(hass, "system_health", {})

    info = await get_system_health_info(hass, DOMAIN)

    for key, val in info.items():
        if asyncio.iscoroutine(val):
            info[key] = await val

    assert info == {"can_reach_server": {"type": "failed", "error": "unreachable"}}
