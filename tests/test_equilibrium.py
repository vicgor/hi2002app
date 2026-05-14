"""Tests for EquilibriumDetector."""

from __future__ import annotations

import pytest

from hi2002app.core.equilibrium import EquilibriumDetector, EquilibriumResult


@pytest.fixture
def detector() -> EquilibriumDetector:
    return EquilibriumDetector(window_size=10, std_threshold=0.02, slope_threshold=0.005)


class TestEquilibriumResult:
    """EquilibriumResult dataclass."""

    def test_fields(self) -> None:
        r = EquilibriumResult(reached=True, window_std=0.01, slope=0.001, samples_in_window=10)
        assert r.reached is True
        assert r.window_std == 0.01


class TestEquilibriumDetector:
    """Core detection logic."""

    def test_not_enough_samples(self, detector: EquilibriumDetector) -> None:
        """Returns reached=False until window is full."""
        for i in range(9):
            result = detector.add_reading(7.0)
            assert result.reached is False
            assert result.samples_in_window == i + 1

    def test_stable_series_reaches_equilibrium(
        self, detector: EquilibriumDetector, stable_ph_series: list[float]
    ) -> None:
        results = [detector.add_reading(ph) for ph in stable_ph_series]
        assert results[-1].reached is True

    def test_unstable_series_does_not_reach_equilibrium(
        self, detector: EquilibriumDetector, unstable_ph_series: list[float]
    ) -> None:
        results = [detector.add_reading(ph) for ph in unstable_ph_series]
        assert results[-1].reached is False

    def test_std_is_low_for_stable(self, detector: EquilibriumDetector) -> None:
        for ph in [7.00] * 10:
            result = detector.add_reading(ph)
        assert result.window_std < 0.001  # noqa: F821 — last loop value

    def test_slope_is_low_for_stable(self, detector: EquilibriumDetector) -> None:
        result = None
        for ph in [7.00] * 10:
            result = detector.add_reading(ph)
        assert result is not None
        assert result.slope < 0.001

    def test_reset_clears_buffer(self, detector: EquilibriumDetector) -> None:
        for ph in [7.0] * 10:
            detector.add_reading(ph)
        detector.reset()
        result = detector.add_reading(7.0)
        assert result.samples_in_window == 1
        assert result.reached is False

    def test_custom_thresholds(self) -> None:
        """Strict thresholds reject mild variation."""
        strict = EquilibriumDetector(window_size=5, std_threshold=0.001, slope_threshold=0.0001)
        # Variation of 0.05 exceeds strict threshold
        for ph in [7.00, 7.05, 7.00, 7.05, 7.00]:
            result = strict.add_reading(ph)
        assert result.reached is False  # noqa: F821

    def test_window_is_rolling(self, detector: EquilibriumDetector) -> None:
        """After unstable start, stable tail should reach equilibrium."""
        # Dump unstable readings to fill window
        for ph in [1.0, 14.0, 1.0, 14.0, 1.0, 14.0, 1.0, 14.0, 1.0, 14.0]:
            detector.add_reading(ph)
        # Now feed stable values — window should roll over
        for ph in [7.00, 7.00, 7.00, 7.00, 7.00, 7.00, 7.00, 7.00, 7.00, 7.00]:
            result = detector.add_reading(ph)
        assert result.reached is True  # noqa: F821
