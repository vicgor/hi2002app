"""pH equilibrium detection using a rolling-window stability criterion.

A measurement is considered at equilibrium when the standard deviation
of the last N pH readings falls below a configurable threshold AND
the absolute slope (linear regression) is below a rate threshold.
"""

from __future__ import annotations

import logging
from collections import deque
from typing import Optional

import numpy as np

from hi2002app.models.measurement import Measurement

log = logging.getLogger(__name__)

_DEFAULT_WINDOW = 10       # number of readings in rolling window
_DEFAULT_STD_THR = 0.02    # pH units — stability threshold
_DEFAULT_SLOPE_THR = 0.005 # pH/s — drift rate threshold


class EquilibriumDetector:
    """Stateful detector that flags measurements at pH equilibrium.

    Args:
        window: Rolling window size (number of measurements).
        std_threshold: Max allowed std deviation (pH units).
        slope_threshold: Max allowed drift slope (pH/s).
    """

    def __init__(
        self,
        window: int = _DEFAULT_WINDOW,
        std_threshold: float = _DEFAULT_STD_THR,
        slope_threshold: float = _DEFAULT_SLOPE_THR,
    ) -> None:
        """Initialise detector with configurable thresholds."""
        self.window = window
        self.std_threshold = std_threshold
        self.slope_threshold = slope_threshold
        self._ph_buf: deque[float] = deque(maxlen=window)
        self._ts_buf: deque[float] = deque(maxlen=window)  # Unix timestamps
        self._equilibrium_count: int = 0

    def reset(self) -> None:
        """Clear internal buffers (e.g. on new titration step)."""
        self._ph_buf.clear()
        self._ts_buf.clear()
        self._equilibrium_count = 0

    @property
    def equilibrium_count(self) -> int:
        """Number of consecutive equilibrium readings."""
        return self._equilibrium_count

    def update(self, m: Measurement) -> Measurement:
        """Process a measurement and return it with at_equilibrium set.

        Args:
            m: Incoming measurement.

        Returns:
            The same measurement object with ``at_equilibrium`` updated.
        """
        self._ph_buf.append(m.ph)
        self._ts_buf.append(m.timestamp.timestamp())

        m.at_equilibrium = self._check_equilibrium()
        if m.at_equilibrium:
            self._equilibrium_count += 1
        else:
            self._equilibrium_count = 0
        return m

    def _check_equilibrium(self) -> bool:
        """Return True if current window satisfies stability criteria."""
        if len(self._ph_buf) < self.window:
            return False

        ph_arr = np.array(self._ph_buf, dtype=float)
        ts_arr = np.array(self._ts_buf, dtype=float)

        # 1. Standard deviation criterion
        if float(np.std(ph_arr)) > self.std_threshold:
            return False

        # 2. Slope criterion (linear regression)
        dt = ts_arr - ts_arr[0]
        if dt[-1] > 0:
            slope = float(np.polyfit(dt, ph_arr, 1)[0])
            if abs(slope) > self.slope_threshold:
                return False

        return True
