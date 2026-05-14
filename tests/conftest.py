"""Shared pytest fixtures for hi2002app tests."""

from __future__ import annotations

from datetime import datetime

import pytest

from hi2002app.models.measurement import Measurement


@pytest.fixture
def sample_measurement() -> Measurement:
    """Return a single sample Measurement."""
    return Measurement(
        timestamp=datetime(2026, 5, 14, 12, 0, 0),
        ph=7.01,
        temperature_c=25.0,
        mv=-0.6,
        volume_ml=1.5,
    )


@pytest.fixture
def stable_ph_series() -> list[float]:
    """10 pH readings with negligible variation — should trigger equilibrium."""
    return [7.00, 7.01, 7.00, 7.01, 7.00, 7.01, 7.00, 7.00, 7.01, 7.00]


@pytest.fixture
def unstable_ph_series() -> list[float]:
    """10 pH readings with large drift — should NOT trigger equilibrium."""
    return [4.0, 4.5, 5.2, 5.9, 6.4, 7.1, 7.8, 8.3, 8.9, 9.5]


@pytest.fixture
def sample_measurements() -> list[Measurement]:
    """Return a list of 5 Measurements for export tests."""
    return [
        Measurement(
            timestamp=datetime(2026, 5, 14, 12, 0, i),
            ph=round(7.0 + i * 0.1, 2),
            temperature_c=25.0,
            mv=round(-i * 6.0, 1),
            volume_ml=round(i * 0.5, 1),
        )
        for i in range(5)
    ]
