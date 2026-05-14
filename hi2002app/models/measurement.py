"""Dataclass representing a single pH measurement."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Measurement:
    """A single reading from the HI2002 pH meter.

    Attributes:
        timestamp: UTC datetime of the reading.
        ph: pH value (0.00 – 14.00).
        temperature: Sample temperature in °C.
        mv: Raw mV value from the electrode.
        volume_ml: Volume of titrant added (mL), used for titration curves.
        at_equilibrium: True when pH stability criterion is met.
    """

    timestamp: datetime = field(default_factory=datetime.utcnow)
    ph: float = 0.0
    temperature: float = 25.0
    mv: float = 0.0
    volume_ml: float = 0.0
    at_equilibrium: bool = False

    def to_dict(self) -> dict[str, object]:
        """Serialize to plain dict."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "ph": self.ph,
            "temperature": self.temperature,
            "mv": self.mv,
            "volume_ml": self.volume_ml,
            "at_equilibrium": self.at_equilibrium,
        }
