"""Tests for DataExporter — CSV, Excel, JSON, Markdown, PDF."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest

from hi2002app.core.exporter import DataExporter
from hi2002app.models.measurement import Measurement


class TestCSVExport:
    def test_creates_file(self, sample_measurements: list[Measurement], tmp_path: Path) -> None:
        out = tmp_path / "data.csv"
        DataExporter.to_csv(sample_measurements, out)
        assert out.exists()

    def test_row_count(self, sample_measurements: list[Measurement], tmp_path: Path) -> None:
        out = tmp_path / "data.csv"
        DataExporter.to_csv(sample_measurements, out)
        with out.open(encoding="utf-8") as fh:
            rows = list(csv.DictReader(fh))
        assert len(rows) == len(sample_measurements)

    def test_ph_values(self, sample_measurements: list[Measurement], tmp_path: Path) -> None:
        out = tmp_path / "data.csv"
        DataExporter.to_csv(sample_measurements, out)
        with out.open(encoding="utf-8") as fh:
            rows = list(csv.DictReader(fh))
        for i, row in enumerate(rows):
            assert float(row["ph"]) == pytest.approx(sample_measurements[i].ph)

    def test_empty_list_no_crash(self, tmp_path: Path) -> None:
        out = tmp_path / "empty.csv"
        DataExporter.to_csv([], out)  # Should not raise, just log warning
        assert not out.exists()  # Nothing written for empty list


class TestJSONExport:
    def test_creates_file(self, sample_measurements: list[Measurement], tmp_path: Path) -> None:
        out = tmp_path / "data.json"
        DataExporter.to_json(sample_measurements, out)
        assert out.exists()

    def test_valid_json(self, sample_measurements: list[Measurement], tmp_path: Path) -> None:
        out = tmp_path / "data.json"
        DataExporter.to_json(sample_measurements, out)
        data = json.loads(out.read_text(encoding="utf-8"))
        assert isinstance(data, list)
        assert len(data) == len(sample_measurements)

    def test_ph_values_in_json(self, sample_measurements: list[Measurement], tmp_path: Path) -> None:
        out = tmp_path / "data.json"
        DataExporter.to_json(sample_measurements, out)
        data = json.loads(out.read_text(encoding="utf-8"))
        for i, item in enumerate(data):
            assert item["ph"] == pytest.approx(sample_measurements[i].ph)

    def test_empty_list(self, tmp_path: Path) -> None:
        out = tmp_path / "empty.json"
        DataExporter.to_json([], out)
        data = json.loads(out.read_text(encoding="utf-8"))
        assert data == []


class TestMarkdownExport:
    def test_creates_file(self, sample_measurements: list[Measurement], tmp_path: Path) -> None:
        out = tmp_path / "data.md"
        DataExporter.to_markdown(sample_measurements, out)
        assert out.exists()

    def test_contains_header(self, sample_measurements: list[Measurement], tmp_path: Path) -> None:
        out = tmp_path / "data.md"
        DataExporter.to_markdown(sample_measurements, out)
        content = out.read_text(encoding="utf-8")
        assert "# HI2002" in content

    def test_contains_table_separator(self, sample_measurements: list[Measurement], tmp_path: Path) -> None:
        out = tmp_path / "data.md"
        DataExporter.to_markdown(sample_measurements, out)
        content = out.read_text(encoding="utf-8")
        assert "|---|" in content

    def test_row_count_in_table(
        self, sample_measurements: list[Measurement], tmp_path: Path
    ) -> None:
        out = tmp_path / "data.md"
        DataExporter.to_markdown(sample_measurements, out)
        lines = out.read_text(encoding="utf-8").splitlines()
        # header line + separator line + N data rows (+ title line)
        data_lines = [l for l in lines if l.startswith("|") and "---" not in l]
        # first data_line is column header, rest are data rows
        assert len(data_lines) - 1 == len(sample_measurements)

    def test_empty_list(self, tmp_path: Path) -> None:
        out = tmp_path / "empty.md"
        DataExporter.to_markdown([], out)
        content = out.read_text(encoding="utf-8")
        assert "No data" in content


class TestExcelExport:
    def test_creates_file(self, sample_measurements: list[Measurement], tmp_path: Path) -> None:
        out = tmp_path / "data.xlsx"
        DataExporter.to_excel(sample_measurements, out)
        assert out.exists()

    def test_row_count(self, sample_measurements: list[Measurement], tmp_path: Path) -> None:
        import openpyxl

        out = tmp_path / "data.xlsx"
        DataExporter.to_excel(sample_measurements, out)
        wb = openpyxl.load_workbook(out)
        ws = wb.active
        # Row 1 = headers, rows 2..N+1 = data
        assert ws.max_row == len(sample_measurements) + 1  # type: ignore[union-attr]

    def test_empty_list(self, tmp_path: Path) -> None:
        out = tmp_path / "empty.xlsx"
        DataExporter.to_excel([], out)
        assert out.exists()


class TestPDFExport:
    def test_creates_file(self, sample_measurements: list[Measurement], tmp_path: Path) -> None:
        out = tmp_path / "data.pdf"
        DataExporter.to_pdf(sample_measurements, out)
        assert out.exists()

    def test_pdf_magic_bytes(self, sample_measurements: list[Measurement], tmp_path: Path) -> None:
        out = tmp_path / "data.pdf"
        DataExporter.to_pdf(sample_measurements, out)
        with out.open("rb") as fh:
            header = fh.read(4)
        assert header == b"%PDF"

    def test_empty_list(self, tmp_path: Path) -> None:
        out = tmp_path / "empty.pdf"
        DataExporter.to_pdf([], out)
        assert out.exists()
