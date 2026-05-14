"""Tests for HI2002 serial line parser (DeviceReader._parse_line)."""

from __future__ import annotations

from datetime import datetime
from unittest.mock import patch

import pytest

from hi2002app.core.device import DeviceReader
from hi2002app.models.measurement import Measurement


@pytest.fixture
def reader() -> DeviceReader:
    """Return a DeviceReader instance (no port opened)."""
    return DeviceReader(port="COM99")  # Non-existent port — parse-only tests


class TestParseLineValid:
    """Valid HI2002 line formats."""

    def test_standard_format(self, reader: DeviceReader) -> None:
        """Parses standard pH/T/mV line correctly."""
        line = "pH  7.01  T  25.0  mV  -12.5"
        m = reader._parse_line(line)  # noqa: SLF001
        assert m is not None
        assert m.ph == pytest.approx(7.01)
        assert m.temperature_c == pytest.approx(25.0)
        assert m.mv == pytest.approx(-12.5)

    def test_positive_mv(self, reader: DeviceReader) -> None:
        line = "pH 4.00 T 20.5 mV 177.5"
        m = reader._parse_line(line)  # noqa: SLF001
        assert m is not None
        assert m.ph == pytest.approx(4.00)
        assert m.mv == pytest.approx(177.5)

    def test_case_insensitive(self, reader: DeviceReader) -> None:
        line = "PH 9.50 t 22.0 MV -148.0"
        m = reader._parse_line(line)  # noqa: SLF001
        assert m is not None
        assert m.ph == pytest.approx(9.50)

    def test_returns_measurement_type(self, reader: DeviceReader) -> None:
        line = "pH 7.00 T 25.0 mV 0.0"
        m = reader._parse_line(line)  # noqa: SLF001
        assert isinstance(m, Measurement)

    def test_timestamp_is_set(self, reader: DeviceReader) -> None:
        line = "pH 7.00 T 25.0 mV 0.0"
        before = datetime.utcnow()
        m = reader._parse_line(line)  # noqa: SLF001
        after = datetime.utcnow()
        assert m is not None
        assert before <= m.timestamp <= after


class TestParseLineInvalid:
    """Lines that should return None."""

    def test_empty_string(self, reader: DeviceReader) -> None:
        assert reader._parse_line("") is None  # noqa: SLF001

    def test_garbage_data(self, reader: DeviceReader) -> None:
        assert reader._parse_line("HELLO WORLD 123") is None  # noqa: SLF001

    def test_partial_line_missing_mv(self, reader: DeviceReader) -> None:
        assert reader._parse_line("pH 7.00 T 25.0") is None  # noqa: SLF001

    def test_non_numeric_ph(self, reader: DeviceReader) -> None:
        # Pattern won't match non-digit pH
        assert reader._parse_line("pH XX T 25.0 mV 0.0") is None  # noqa: SLF001


class TestDemoMode:
    """DeviceReader demo mode API."""

    def test_set_demo_mode(self, reader: DeviceReader) -> None:
        reader.set_demo_mode(True)
        assert reader._demo_mode is True  # noqa: SLF001

    def test_stop_reading(self, reader: DeviceReader) -> None:
        reader._running = True  # noqa: SLF001
        reader.stop_reading()
        assert reader._running is False  # noqa: SLF001
