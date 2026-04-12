"""Pytest fixtures for the vtherm_climate_replication test suite."""

from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable loading custom integrations from this repository in all tests."""
    yield