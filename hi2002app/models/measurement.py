"""Measurement dataclass — one pH reading."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Measurement:
    """Single pH measurement captured from the HI2002 device.

    Attributes:
        timestamp: UTC time of measurement.
        ph: pH value (0–14).
        temperature_c: Temperature in degrees Celsius (if available).
        mv: Raw mV value from electrode.
        volume_ml: Volume of titrant added (mL) — for titration curves.
        equilibrium_reached: True when stability algorithm confirms equilibrium.
    """

    timestamp: datetime = field(default_factory=datetime.utcnow)
    ph: float = 0.0
    temperature_c: float | None = None
    mv: float | None = None
    volume_ml: float = 0.0
    equilibrium_reached: bool = False

    def to_dict(self) -> dict[str, object]:
        """Serialise to plain dict for export."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "ph": self.ph,
            "temperature_c": self.temperature_c,
            "mv": self.mv,
            "volume_ml": self.volume_ml,
            "equilibrium_reached": self.equilibrium_reached,
        }
