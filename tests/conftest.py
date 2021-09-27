"""Global fixtures for Reaper integration."""
import json
from unittest.mock import patch

import pytest
from pytest_homeassistant_custom_component.common import load_fixture

from custom_components.reaper import ReaperError


@pytest.fixture(name="bypass_get_data")
def bypass_get_data_fixture():
    """Skip calls to get data from API."""
    with patch(
        "custom_components.reaper.Reaper.getStatus",
        return_value=json.loads(load_fixture("reaper_status_data.json")),
    ):
        yield


@pytest.fixture(name="error_on_get_data")
def error_get_data_fixture():
    """Simulate error when retrieving data from API."""
    with patch(
        "custom_components.reaper.Reaper.getStatus",
        side_effect=ReaperError(500, "exception"),
    ):
        yield


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    yield
