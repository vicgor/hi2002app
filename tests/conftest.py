"""Shared pytest fixtures."""

from __future__ import annotations

from datetime import datetime, timedelta

import pytest

from hi2002app.models.measurement import Measurement


@pytest.fixture
def sample_measurements() -> list[Measurement]:
    """Return a list of 5 realistic Measurement instances for testing."""
    base = datetime(2024, 1, 1, 12, 0, 0)
    return [
        Measurement(
            timestamp=base + timedelta(seconds=i * 10),
            ph=round(4.0 + i * 0.5, 3),
            temperature_c=25.0,
            mv=round(177.5 - i * 29.58, 1),
            volume_ml=round(i * 0.5, 2),
        )
        for i in range(5)
    ]
