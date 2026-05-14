"""Equilibrium detection algorithm for pH stabilisation."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass


@dataclass
class EquilibriumResult:
    """Result of a single equilibrium check.

    Attributes:
        reached: True when equilibrium criteria are met.
        window_std: Standard deviation of pH over the analysis window.
        slope: Absolute rate of change (pH/sample).
        samples_in_window: Number of samples used.
    """

    reached: bool
    window_std: float
    slope: float
    samples_in_window: int


class EquilibriumDetector:
    """Detect when the pH reading has stabilised.

    Uses a rolling window.  Equilibrium is declared when *both*:
    - The standard deviation of pH in the window is below ``std_threshold``.
    - The absolute linear slope is below ``slope_threshold`` (pH / sample).

    Parameters:
        window_size: Number of consecutive readings to evaluate.
        std_threshold: Maximum allowed std deviation (default 0.02 pH units).
        slope_threshold: Maximum allowed slope (default 0.005 pH/sample).
    """

    def __init__(
        self,
        window_size: int = 10,
        std_threshold: float = 0.02,
        slope_threshold: float = 0.005,
    ) -> None:
        """Initialise the detector."""
        self.window_size = window_size
        self.std_threshold = std_threshold
        self.slope_threshold = slope_threshold
        self._buffer: deque[float] = deque(maxlen=window_size)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def reset(self) -> None:
        """Clear the internal buffer (call before a new titration)."""
        self._buffer.clear()

    def add_reading(self, ph: float) -> EquilibriumResult:
        """Add a new pH reading and evaluate equilibrium.

        Returns:
            EquilibriumResult with the current stability assessment.
        """
        self._buffer.append(ph)
        n = len(self._buffer)

        if n < self.window_size:
            return EquilibriumResult(
                reached=False,
                window_std=0.0,
                slope=0.0,
                samples_in_window=n,
            )

        values = list(self._buffer)
        mean = sum(values) / n
        variance = sum((v - mean) ** 2 for v in values) / n
        std = variance**0.5

        # Simple linear regression slope
        xs = list(range(n))
        x_mean = (n - 1) / 2.0
        numerator = sum((xs[i] - x_mean) * (values[i] - mean) for i in range(n))
        denominator = sum((x - x_mean) ** 2 for x in xs)
        slope = abs(numerator / denominator) if denominator > 0 else 0.0

        reached = std <= self.std_threshold and slope <= self.slope_threshold
        return EquilibriumResult(
            reached=reached,
            window_std=round(std, 5),
            slope=round(slope, 6),
            samples_in_window=n,
        )
