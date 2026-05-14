"""Tests for EquilibriumDetector."""

from __future__ import annotations

import math

import pytest

from hi2002app.core.equilibrium import EquilibriumDetector, EquilibriumResult


@pytest.fixture
def detector() -> EquilibriumDetector:
    """Return a default EquilibriumDetector."""
    return EquilibriumDetector(window_size=5, std_threshold=0.02, slope_threshold=0.005)


class TestEquilibriumDetector:
    def test_not_reached_before_window_full(self, detector: EquilibriumDetector) -> None:
        for _ in range(4):
            result = detector.add_reading(7.0)
        assert not result.reached
        assert result.samples_in_window == 4

    def test_reached_on_stable_readings(self, detector: EquilibriumDetector) -> None:
        for _ in range(5):
            result = detector.add_reading(7.000)
        assert result.reached
        assert result.window_std == pytest.approx(0.0, abs=1e-6)

    def test_not_reached_on_noisy_readings(self, detector: EquilibriumDetector) -> None:
        values = [7.0, 7.1, 6.9, 7.2, 6.8]
        for v in values:
            result = detector.add_reading(v)
        assert not result.reached

    def test_reset_clears_buffer(self, detector: EquilibriumDetector) -> None:
        for _ in range(5):
            detector.add_reading(7.0)
        detector.reset()
        result = detector.add_reading(7.0)
        assert result.samples_in_window == 1
        assert not result.reached

    def test_returns_equilibrium_result_type(self, detector: EquilibriumDetector) -> None:
        result = detector.add_reading(7.0)
        assert isinstance(result, EquilibriumResult)

    def test_nan_is_ignored(self, detector: EquilibriumDetector) -> None:
        result = detector.add_reading(float("nan"))
        assert not result.reached
        assert result.samples_in_window == 0

    def test_inf_is_ignored(self, detector: EquilibriumDetector) -> None:
        result = detector.add_reading(float("inf"))
        assert not result.reached

    def test_out_of_range_is_ignored(self, detector: EquilibriumDetector) -> None:
        result = detector.add_reading(999.9)
        assert not result.reached
        assert result.samples_in_window == 0

    def test_boundary_ph_zero(self, detector: EquilibriumDetector) -> None:
        for _ in range(5):
            result = detector.add_reading(0.0)
        assert result.reached

    def test_boundary_ph_fourteen(self, detector: EquilibriumDetector) -> None:
        for _ in range(5):
            result = detector.add_reading(14.0)
        assert result.reached

    def test_slope_detection(self, detector: EquilibriumDetector) -> None:
        """Monotonically rising values should not reach equilibrium."""
        for i in range(5):
            result = detector.add_reading(7.0 + i * 0.05)
        assert not result.reached
        assert result.slope > detector.slope_threshold

    def test_window_std_in_result(self, detector: EquilibriumDetector) -> None:
        for _ in range(5):
            detector.add_reading(7.0)
        result = detector.add_reading(7.0)
        assert result.window_std >= 0.0
        assert math.isfinite(result.window_std)
