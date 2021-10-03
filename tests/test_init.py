"""Test init of Reaper integration."""
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.reaper.const import (
    CONF_HOSTNAME,
    CONF_PASSWORD,
    CONF_PORT,
    CONF_UPDATE_INTERVAL,
    CONF_USERNAME,
    DOMAIN,
)
from homeassistant.config_entries import ConfigEntryState


async def test_config_entry_not_ready(hass, error_on_get_data):
    """Test for setup failure if connection to Reaper is missing."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_HOSTNAME: "192.168.0.5",
            CONF_PORT: 8080,
            CONF_USERNAME: "admin",
            CONF_PASSWORD: "pass",
            CONF_UPDATE_INTERVAL: 60,
        },
    )
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)

    assert entry.state == ConfigEntryState.SETUP_RETRY


async def test_unload_entry(hass):
    """Test successful unload of entry."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_HOSTNAME: "192.168.0.5",
            CONF_PORT: 8080,
            CONF_USERNAME: "",
            CONF_PASSWORD: "",
            CONF_UPDATE_INTERVAL: 60,
        },
    )
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    assert len(hass.config_entries.async_entries(DOMAIN)) == 1
    assert entry.state == ConfigEntryState.SETUP_RETRY

    assert await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()

    assert entry.state == ConfigEntryState.NOT_LOADED
    assert not hass.data.get(DOMAIN)
