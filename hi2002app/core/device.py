"""Serial communication with Hanna HI2002 pH meter.

The HI2002 outputs data over RS-232 at 1200 baud, 7 data bits,
even parity, 1 stop bit (7E1). Each line is terminated with CR+LF
and contains pH, mV and temperature values.

Example output line:  pH= 7.01  mV= -3.2  T= 25.1 C
"""

from __future__ import annotations

import logging
import re
import time
from datetime import datetime
from typing import Optional

import serial
from PySide6.QtCore import QObject, QThread, Signal

from hi2002app.models.measurement import Measurement

log = logging.getLogger(__name__)

# Default HI2002 serial parameters
_BAUD = 1200
_BYTESIZE = serial.SEVENBITS
_PARITY = serial.PARITY_EVEN
_STOPBITS = serial.STOPBITS_ONE
_TIMEOUT = 2.0  # seconds

# Regex for parsing a HI2002 output line
_LINE_RE = re.compile(
    r"pH=\s*(?P<ph>[\-0-9.]+)"
    r".*?mV=\s*(?P<mv>[\-0-9.]+)"
    r".*?T=\s*(?P<temp>[\-0-9.]+)",
    re.IGNORECASE,
)


class DeviceReader(QObject):
    """Reads measurements from HI2002 in a background QThread.

    Signals:
        measurement_ready: Emitted for each successfully parsed measurement.
        error_occurred: Emitted when a serial or parse error occurs.
        connection_changed: Emitted when connection state changes (True=connected).
    """

    measurement_ready: Signal = Signal(object)   # Measurement
    error_occurred: Signal = Signal(str)
    connection_changed: Signal = Signal(bool)

    def __init__(self, parent: Optional[QObject] = None) -> None:
        """Initialise the reader (not yet connected)."""
        super().__init__(parent)
        self._port: str = ""
        self._running: bool = False
        self._serial: Optional[serial.Serial] = None
        self._thread: Optional[QThread] = None
        self._volume_ml: float = 0.0  # current titrant volume

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def set_port(self, port: str) -> None:
        """Set the serial port name (e.g. 'COM3')."""
        self._port = port

    def set_volume(self, volume_ml: float) -> None:
        """Update current titrant volume (called externally during titration)."""
        self._volume_ml = volume_ml

    def start(self) -> None:
        """Open the serial port and start reading in a QThread."""
        if self._running:
            return
        self._thread = QThread()
        self.moveToThread(self._thread)
        self._thread.started.connect(self._run)
        self._thread.start()

    def stop(self) -> None:
        """Stop reading and close the port."""
        self._running = False
        if self._thread:
            self._thread.quit()
            self._thread.wait(3000)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _run(self) -> None:
        """Main loop executed in the worker thread."""
        try:
            self._serial = serial.Serial(
                port=self._port,
                baudrate=_BAUD,
                bytesize=_BYTESIZE,
                parity=_PARITY,
                stopbits=_STOPBITS,
                timeout=_TIMEOUT,
            )
            self._running = True
            self.connection_changed.emit(True)
            log.info("Connected to HI2002 on %s", self._port)
        except serial.SerialException as exc:
            log.error("Cannot open port %s: %s", self._port, exc)
            self.error_occurred.emit(str(exc))
            return

        while self._running:
            try:
                raw = self._serial.readline()
                if raw:
                    m = self._parse(raw)
                    if m:
                        self.measurement_ready.emit(m)
            except serial.SerialException as exc:
                log.error("Serial read error: %s", exc)
                self.error_occurred.emit(str(exc))
                self._running = False

        if self._serial and self._serial.is_open:
            self._serial.close()
        self.connection_changed.emit(False)
        log.info("Disconnected from HI2002")

    def _parse(self, raw: bytes) -> Optional[Measurement]:
        """Parse a raw byte line into a Measurement."""
        try:
            line = raw.decode("ascii", errors="ignore").strip()
        except Exception:
            return None
        m = _LINE_RE.search(line)
        if not m:
            return None
        try:
            return Measurement(
                timestamp=datetime.utcnow(),
                ph=float(m.group("ph")),
                mv=float(m.group("mv")),
                temperature=float(m.group("temp")),
                volume_ml=self._volume_ml,
            )
        except ValueError:
            return None
