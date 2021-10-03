"""Test sensor of Reaper integration."""
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.reaper.const import (
    CONF_HOSTNAME,
    CONF_PASSWORD,
    CONF_PORT,
    CONF_UPDATE_INTERVAL,
    CONF_USERNAME,
    DOMAIN,
)
from homeassistant.const import STATE_OFF, STATE_ON
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er


async def test_switch(hass: HomeAssistant, bypass_get_data):
    """Test switch."""
    registry = er.async_get(hass)

    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_HOSTNAME: "192.168.0.5",
            CONF_PORT: 9999,
            CONF_USERNAME: "",
            CONF_PASSWORD: "",
            CONF_UPDATE_INTERVAL: 30,
        },
    )
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    state = hass.states.get("switch.recording")

    assert state
    assert state.state == STATE_OFF
    assert state.attributes.get("icon") == "mdi:circle"

    entry = registry.async_get("switch.recording")

    assert entry
    assert entry.unique_id == "192.168.0.5-recording"

    state = hass.states.get("switch.metronome")

    assert state
    assert state.state == STATE_ON
    assert state.attributes.get("icon") == "mdi:metronome"

    entry = registry.async_get("switch.metronome")

    assert entry
    assert entry.unique_id == "192.168.0.5-metronome"

    state = hass.states.get("switch.repeat")

    assert state
    assert state.state == STATE_ON
    assert state.attributes.get("icon") == "mdi:repeat"

    entry = registry.async_get("switch.repeat")

    assert entry
    assert entry.unique_id == "192.168.0.5-repeat"
