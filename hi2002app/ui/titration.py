"""Titration curve widget with dpH/dV derivative display."""

from __future__ import annotations

import numpy as np
import pyqtgraph as pg
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGroupBox, QSplitter, QVBoxLayout, QWidget

from hi2002app.models.measurement import Measurement


class TitrationWidget(QWidget):
    """Displays the pH vs. volume titration curve and its first derivative dpH/dV."""

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialise the titration widget."""
        super().__init__(parent)
        self._volumes: list[float] = []
        self._ph_values: list[float] = []
        self._build_ui()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def add_point(self, m: Measurement) -> None:
        """Add a new measurement point to the titration curve."""
        self._volumes.append(m.volume_ml)
        self._ph_values.append(m.ph)
        self._redraw()

    def clear_data(self) -> None:
        """Reset the titration data."""
        self._volumes.clear()
        self._ph_values.clear()
        self._main_curve.setData([], [])
        self._deriv_curve.setData([], [])
        self._ep_scatter.setData([], [])

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        """Build the split plot layout."""
        layout = QVBoxLayout(self)

        splitter = QSplitter(Qt.Orientation.Vertical)

        # --- Main titration plot ---
        main_box = QGroupBox(self.tr("Titration Curve (pH vs. Volume)"))
        main_layout = QVBoxLayout(main_box)
        self._main_plot = pg.PlotWidget()
        self._main_plot.setLabel("left", "pH")
        self._main_plot.setLabel("bottom", self.tr("Volume (mL)"))
        self._main_plot.setYRange(0, 14)
        self._main_plot.showGrid(x=True, y=True, alpha=0.3)
        self._main_plot.addLine(y=7.0, pen=pg.mkPen(color="#4f98a3", style=Qt.PenStyle.DashLine))
        self._main_curve = self._main_plot.plot(
            pen=pg.mkPen(color="#6daa45", width=2),
            name="pH",
        )
        # Equivalence point scatter
        self._ep_scatter = pg.ScatterPlotItem(
            size=12, brush=pg.mkBrush("#fdab43"), pen=pg.mkPen(None)
        )
        self._main_plot.addItem(self._ep_scatter)
        main_layout.addWidget(self._main_plot)
        splitter.addWidget(main_box)

        # --- Derivative plot ---
        deriv_box = QGroupBox(self.tr("First Derivative dpH/dV"))
        deriv_layout = QVBoxLayout(deriv_box)
        self._deriv_plot = pg.PlotWidget()
        self._deriv_plot.setLabel("left", "dpH/dV")
        self._deriv_plot.setLabel("bottom", self.tr("Volume (mL)"))
        self._deriv_plot.showGrid(x=True, y=True, alpha=0.3)
        self._deriv_curve = self._deriv_plot.plot(
            pen=pg.mkPen(color="#dd6974", width=2),
            name="dpH/dV",
        )
        deriv_layout.addWidget(self._deriv_plot)
        splitter.addWidget(deriv_box)

        layout.addWidget(splitter)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _redraw(self) -> None:
        """Recompute and refresh both plots."""
        v = self._volumes
        ph = self._ph_values

        self._main_curve.setData(v, ph)

        if len(v) < 3:
            return

        arr_v = np.array(v)
        arr_ph = np.array(ph)

        # dpH/dV via central differences
        dv = np.gradient(arr_v)
        dph = np.gradient(arr_ph)
        # Avoid division by zero
        mask = dv != 0
        deriv = np.zeros_like(dph)
        deriv[mask] = dph[mask] / dv[mask]

        self._deriv_curve.setData(arr_v.tolist(), deriv.tolist())

        # Mark equivalence point (max of |dpH/dV|)
        idx_ep = int(np.argmax(np.abs(deriv)))
        self._ep_scatter.setData(
            x=[arr_v[idx_ep]],
            y=[arr_ph[idx_ep]],
        )
