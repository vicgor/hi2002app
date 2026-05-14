"""Export measurement data to CSV, Excel, JSON, Markdown and PDF."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Sequence

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from hi2002app.models.measurement import Measurement

log = logging.getLogger(__name__)


class DataExporter:
    """Converts a list of Measurement objects to various file formats."""

    def __init__(self, measurements: Sequence[Measurement]) -> None:
        """Initialise exporter with the dataset to export."""
        self._data = list(measurements)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def to_csv(self, path: Path) -> None:
        """Export to CSV."""
        self._to_dataframe().to_csv(path, index=False, encoding="utf-8")
        log.info("Exported CSV: %s", path)

    def to_excel(self, path: Path) -> None:
        """Export to Excel (.xlsx)."""
        df = self._to_dataframe()
        with pd.ExcelWriter(path, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Measurements")
            # Auto-fit column widths
            ws = writer.sheets["Measurements"]
            for col in ws.columns:
                max_len = max(len(str(cell.value or "")) for cell in col)
                ws.column_dimensions[col[0].column_letter].width = max_len + 4
        log.info("Exported Excel: %s", path)

    def to_json(self, path: Path) -> None:
        """Export to JSON array."""
        path.write_text(
            json.dumps([m.to_dict() for m in self._data], indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        log.info("Exported JSON: %s", path)

    def to_markdown(self, path: Path) -> None:
        """Export to Markdown table."""
        lines = [
            "# HI2002 Measurement Data\n",
            "| Timestamp | pH | Temperature (°C) | mV | Volume (mL) | Equilibrium |",
            "|-----------|-----|------------------|----|-------------|-------------|\n",
        ]
        for m in self._data:
            eq = "✓" if m.at_equilibrium else ""
            lines.append(
                f"| {m.timestamp.isoformat()} "
                f"| {m.ph:.3f} "
                f"| {m.temperature:.1f} "
                f"| {m.mv:.1f} "
                f"| {m.volume_ml:.2f} "
                f"| {eq} |\n"
            )
        path.write_text("".join(lines), encoding="utf-8")
        log.info("Exported Markdown: %s", path)

    def to_pdf(self, path: Path, title: str = "HI2002 Titration Report") -> None:
        """Export to PDF with a formatted table."""
        doc = SimpleDocTemplate(
            str(path),
            pagesize=A4,
            leftMargin=2 * cm,
            rightMargin=2 * cm,
            topMargin=2 * cm,
            bottomMargin=2 * cm,
        )
        styles = getSampleStyleSheet()
        story = [
            Paragraph(title, styles["Title"]),
            Spacer(1, 0.5 * cm),
        ]
        headers = ["Timestamp", "pH", "Temp °C", "mV", "Vol mL", "Eq"]
        rows = [headers] + [
            [
                m.timestamp.strftime("%H:%M:%S"),
                f"{m.ph:.3f}",
                f"{m.temperature:.1f}",
                f"{m.mv:.1f}",
                f"{m.volume_ml:.2f}",
                "✓" if m.at_equilibrium else "",
            ]
            for m in self._data
        ]
        tbl = Table(rows, repeatRows=1)
        tbl.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2563eb")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f1f5f9")]),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
            ])
        )
        story.append(tbl)
        doc.build(story)
        log.info("Exported PDF: %s", path)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _to_dataframe(self) -> pd.DataFrame:
        """Convert measurements to a pandas DataFrame."""
        return pd.DataFrame([m.to_dict() for m in self._data])
