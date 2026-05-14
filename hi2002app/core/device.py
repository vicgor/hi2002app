"""HI2002 serial device reader running in a background QThread."""

from __future__ import annotations

import logging
import re
import time
from datetime import datetime
from typing import ClassVar

import serial
from PySide6.QtCore import QThread, Signal

from hi2002app.models.measurement import Measurement

logger = logging.getLogger(__name__)

# HI2002 sends lines like:  "pH  7.01  T  25.0  mV  -12.5\r\n"
# Adjust the pattern to the actual HI2002 output format.
_LINE_PATTERN: re.Pattern[str] = re.compile(
    r"pH\s+(?P<ph>[\d.]+).*?T\s+(?P<temp>[\d.]+).*?mV\s+(?P<mv>[\-\d.]+)",
    re.IGNORECASE,
)


class DeviceReader(QThread):
    """Background thread that reads measurements from the HI2002 via RS-232.

    Signals:
        measurement_ready: Emitted with every successfully parsed Measurement.
        error_occurred: Emitted with a human-readable error string.
        connected: Emitted when the port opens successfully.
        disconnected: Emitted when the port is closed or lost.
    """

    measurement_ready: ClassVar[Signal] = Signal(Measurement)
    error_occurred: ClassVar[Signal] = Signal(str)
    connected: ClassVar[Signal] = Signal()
    disconnected: ClassVar[Signal] = Signal()

    # HI2002 default serial params
    DEFAULT_BAUD: int = 1200
    DEFAULT_BYTESIZE: int = 7
    DEFAULT_PARITY: str = serial.PARITY_EVEN
    DEFAULT_STOPBITS: float = serial.STOPBITS_ONE
    POLL_INTERVAL_S: float = 1.0

    def __init__(
        self,
        port: str = "COM1",
        baud_rate: int = DEFAULT_BAUD,
        poll_interval: float = POLL_INTERVAL_S,
    ) -> None:
        """Initialise the reader."""
        super().__init__()
        self.port = port
        self.baud_rate = baud_rate
        self.poll_interval = poll_interval
        self._running = False
        self._demo_mode = False  # Set True when no physical device present
        self._demo_ph: float = 7.0

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def set_demo_mode(self, enabled: bool) -> None:
        """Enable demo/simulation mode (no physical device needed)."""
        self._demo_mode = enabled

    def stop_reading(self) -> None:
        """Request the reading loop to stop."""
        self._running = False

    # ------------------------------------------------------------------
    # QThread.run
    # ------------------------------------------------------------------

    def run(self) -> None:  # noqa: C901
        """Main loop — called by QThread.start()."""
        self._running = True

        if self._demo_mode:
            self._demo_loop()
            return

        try:
            port = serial.Serial(
                port=self.port,
                baudrate=self.baud_rate,
                bytesize=self.DEFAULT_BYTESIZE,
                parity=self.DEFAULT_PARITY,
                stopbits=self.DEFAULT_STOPBITS,
                timeout=2,
            )
        except serial.SerialException as exc:
            logger.error("Cannot open serial port %s: %s", self.port, exc)
            self.error_occurred.emit(str(exc))
            return

        self.connected.emit()
        logger.info("Connected to HI2002 on %s at %d baud", self.port, self.baud_rate)

        try:
            while self._running:
                try:
                    raw = port.readline().decode("ascii", errors="replace").strip()
                    if raw:
                        m = self._parse_line(raw)
                        if m:
                            self.measurement_ready.emit(m)
                except serial.SerialException as exc:
                    logger.error("Serial read error: %s", exc)
                    self.error_occurred.emit(str(exc))
                    break
                time.sleep(self.poll_interval)
        finally:
            port.close()
            self.disconnected.emit()
            logger.info("Disconnected from HI2002")

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _parse_line(self, line: str) -> Measurement | None:
        """Parse a raw serial line from HI2002 into a Measurement."""
        match = _LINE_PATTERN.search(line)
        if not match:
            logger.debug("Unrecognised line: %r", line)
            return None
        try:
            return Measurement(
                timestamp=datetime.utcnow(),
                ph=float(match.group("ph")),
                temperature_c=float(match.group("temp")),
                mv=float(match.group("mv")),
            )
        except ValueError as exc:
            logger.warning("Parse error on line %r: %s", line, exc)
            return None

    def _demo_loop(self) -> None:
        """Simulate HI2002 output for testing without hardware."""
        import math
        import random

        step = 0
        logger.info("Demo mode active")
        self.connected.emit()
        while self._running:
            # Slowly drift pH from 4 to 10 (simulate titration)
            self._demo_ph = 4.0 + 6.0 * (1 - math.exp(-step / 80.0)) + random.gauss(0, 0.02)
            self._demo_ph = max(0.0, min(14.0, self._demo_ph))
            m = Measurement(
                timestamp=datetime.utcnow(),
                ph=round(self._demo_ph, 3),
                temperature_c=round(25.0 + random.gauss(0, 0.1), 1),
                mv=round(-59.16 * (self._demo_ph - 7.0), 1),
                volume_ml=round(step * 0.1, 2),
            )
            self.measurement_ready.emit(m)
            step += 1
            time.sleep(self.poll_interval)
        self.disconnected.emit()
