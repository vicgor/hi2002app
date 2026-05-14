"""Dashboard widget — real-time pH display and live plot."""

from __future__ import annotations

from collections import deque
from typing import ClassVar

import pyqtgraph as pg
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGridLayout, QGroupBox, QLabel, QVBoxLayout, QWidget

from hi2002app.core.equilibrium import EquilibriumResult
from hi2002app.models.measurement import Measurement

_MAX_POINTS = 300  # rolling window for live plot


class DashboardWidget(QWidget):
    """Displays real-time pH value, temperature, mV and a live trend plot."""

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialise the dashboard."""
        super().__init__(parent)
        self._ph_history: deque[float] = deque(maxlen=_MAX_POINTS)
        self._build_ui()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def update_measurement(self, m: Measurement, result: EquilibriumResult) -> None:
        """Refresh all widgets with a new measurement."""
        self._lbl_ph_value.setText(f"{m.ph:.3f}")
        self._lbl_temp.setText(
            f"{m.temperature_c:.1f} °C" if m.temperature_c is not None else "—"
        )
        self._lbl_mv.setText(f"{m.mv:.1f} mV" if m.mv is not None else "—")
        self._lbl_std.setText(f"σ = {result.window_std:.4f}")
        eq_text = self.tr("✓ Equilibrium reached") if result.reached else self.tr("Stabilising…")
        self._lbl_eq.setText(eq_text)
        self._lbl_eq.setProperty("equilibrium", result.reached)
        self._lbl_eq.style().unpolish(self._lbl_eq)
        self._lbl_eq.style().polish(self._lbl_eq)

        self._ph_history.append(m.ph)
        self._curve.setData(list(self._ph_history))

        # Draw equilibrium zone
        if result.reached and len(self._ph_history) > 0:
            last_ph = list(self._ph_history)[-1]
            self._eq_line.setPos(last_ph)
            self._eq_line.setVisible(True)

    def reset(self) -> None:
        """Clear all displayed data."""
        self._ph_history.clear()
        self._curve.setData([])
        self._eq_line.setVisible(False)
        self._lbl_ph_value.setText("—")
        self._lbl_temp.setText("—")
        self._lbl_mv.setText("—")
        self._lbl_std.setText("")
        self._lbl_eq.setText("")

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        """Build widget layout."""
        layout = QVBoxLayout(self)

        # --- KPI cards ---
        kpi_box = QGroupBox(self.tr("Current Reading"))
        kpi_grid = QGridLayout(kpi_box)

        self._lbl_ph_value = self._make_big_label("—")
        self._lbl_temp = self._make_value_label("—")
        self._lbl_mv = self._make_value_label("—")
        self._lbl_std = self._make_value_label("")
        self._lbl_eq = self._make_value_label("")

        kpi_grid.addWidget(QLabel(self.tr("pH")), 0, 0, Qt.AlignmentFlag.AlignCenter)
        kpi_grid.addWidget(self._lbl_ph_value, 1, 0, Qt.AlignmentFlag.AlignCenter)

        kpi_grid.addWidget(QLabel(self.tr("Temperature")), 0, 1, Qt.AlignmentFlag.AlignCenter)
        kpi_grid.addWidget(self._lbl_temp, 1, 1, Qt.AlignmentFlag.AlignCenter)

        kpi_grid.addWidget(QLabel("mV"), 0, 2, Qt.AlignmentFlag.AlignCenter)
        kpi_grid.addWidget(self._lbl_mv, 1, 2, Qt.AlignmentFlag.AlignCenter)

        kpi_grid.addWidget(QLabel(self.tr("Std Dev")), 0, 3, Qt.AlignmentFlag.AlignCenter)
        kpi_grid.addWidget(self._lbl_std, 1, 3, Qt.AlignmentFlag.AlignCenter)

        kpi_grid.addWidget(self._lbl_eq, 1, 4, Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(kpi_box)

        # --- Live pH plot ---
        plot_box = QGroupBox(self.tr("Live pH Trend"))
        plot_layout = QVBoxLayout(plot_box)

        pg.setConfigOption("background", "#1c1b19")
        pg.setConfigOption("foreground", "#cdccca")

        self._plot_widget = pg.PlotWidget()
        self._plot_widget.setLabel("left", "pH")
        self._plot_widget.setLabel("bottom", self.tr("Sample #"))
        self._plot_widget.setYRange(0, 14)
        self._plot_widget.showGrid(x=True, y=True, alpha=0.3)
        self._plot_widget.addLine(y=7.0, pen=pg.mkPen(color="#4f98a3", style=Qt.PenStyle.DashLine))

        self._curve = self._plot_widget.plot(
            pen=pg.mkPen(color="#6daa45", width=2),
            name="pH",
        )
        self._eq_line = pg.InfiniteLine(
            angle=0, movable=False,
            pen=pg.mkPen(color="#fdab43", style=Qt.PenStyle.DotLine, width=1)
        )
        self._eq_line.setVisible(False)
        self._plot_widget.addItem(self._eq_line)

        plot_layout.addWidget(self._plot_widget)
        layout.addWidget(plot_box)

    @staticmethod
    def _make_big_label(text: str) -> QLabel:
        """Create a large numeric display label."""
        lbl = QLabel(text)
        lbl.setObjectName("bigValue")
        return lbl

    @staticmethod
    def _make_value_label(text: str) -> QLabel:
        """Create a standard value display label."""
        lbl = QLabel(text)
        lbl.setObjectName("valueLabel")
        return lbl
