"""MainWindow — application shell with toolbar, status bar and tab area."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import ClassVar

from PySide6.QtCore import QSettings, QSize, Qt, Slot
from PySide6.QtGui import QAction, QCloseEvent
from PySide6.QtWidgets import (
    QFileDialog,
    QLabel,
    QMainWindow,
    QMessageBox,
    QStatusBar,
    QTabWidget,
    QToolBar,
)

from hi2002app.core.device import DeviceReader
from hi2002app.core.equilibrium import EquilibriumDetector
from hi2002app.core.exporter import DataExporter
from hi2002app.models.measurement import Measurement
from hi2002app.ui.dashboard import DashboardWidget
from hi2002app.ui.settings_dlg import SettingsDialog
from hi2002app.ui.titration import TitrationWidget

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """Top-level application window.

    Responsibilities:
    - Host DashboardWidget and TitrationWidget in a QTabWidget.
    - Own the DeviceReader QThread and EquilibriumDetector.
    - Provide toolbar actions: connect/disconnect, export, settings.
    - Persist window geometry via QSettings.
    """

    MIN_SIZE: ClassVar[QSize] = QSize(1024, 680)

    def __init__(self, dark_mode: bool = False) -> None:
        """Initialise the main window."""
        super().__init__()
        self._dark_mode = dark_mode
        self._measurements: list[Measurement] = []
        self._reader: DeviceReader | None = None
        self._equilibrium = EquilibriumDetector()

        self.setMinimumSize(self.MIN_SIZE)
        self.setWindowTitle(self.tr("Hanna HI2002 pH Meter"))

        self._build_ui()
        self._restore_geometry()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        """Build all widgets and layouts."""
        # Central tab widget
        self._tabs = QTabWidget()
        self._dashboard = DashboardWidget()
        self._titration = TitrationWidget()
        self._tabs.addTab(self._dashboard, self.tr("Dashboard"))
        self._tabs.addTab(self._titration, self.tr("Titration Curve"))
        self.setCentralWidget(self._tabs)

        # Toolbar
        toolbar = QToolBar(self.tr("Main"))
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        self._act_connect = QAction(self.tr("Connect"), self)
        self._act_connect.triggered.connect(self._on_connect)
        toolbar.addAction(self._act_connect)

        self._act_disconnect = QAction(self.tr("Disconnect"), self)
        self._act_disconnect.setEnabled(False)
        self._act_disconnect.triggered.connect(self._on_disconnect)
        toolbar.addAction(self._act_disconnect)

        toolbar.addSeparator()

        act_demo = QAction(self.tr("Demo Mode"), self)
        act_demo.triggered.connect(self._on_demo_mode)
        toolbar.addAction(act_demo)

        toolbar.addSeparator()

        act_export = QAction(self.tr("Export…"), self)
        act_export.triggered.connect(self._on_export)
        toolbar.addAction(act_export)

        act_clear = QAction(self.tr("Clear Data"), self)
        act_clear.triggered.connect(self._on_clear)
        toolbar.addAction(act_clear)

        toolbar.addSeparator()

        act_settings = QAction(self.tr("Settings"), self)
        act_settings.triggered.connect(self._on_settings)
        toolbar.addAction(act_settings)

        # Status bar
        self._status = QStatusBar()
        self.setStatusBar(self._status)
        self._lbl_status = QLabel(self.tr("Not connected"))
        self._lbl_ph = QLabel("pH —")
        self._lbl_eq = QLabel("")
        self._status.addWidget(self._lbl_status)
        self._status.addPermanentWidget(self._lbl_eq)
        self._status.addPermanentWidget(self._lbl_ph)

    # ------------------------------------------------------------------
    # Slots — toolbar actions
    # ------------------------------------------------------------------

    @Slot()
    def _on_connect(self) -> None:
        """Open serial port and start reading."""
        settings = QSettings()
        port: str = settings.value("device/port", "COM1", type=str)  # type: ignore[call-overload]
        baud: int = settings.value("device/baud", 1200, type=int)  # type: ignore[call-overload]
        self._start_reader(port=port, baud=baud, demo=False)

    @Slot()
    def _on_demo_mode(self) -> None:
        """Start in demo (simulation) mode."""
        self._start_reader(port="", baud=0, demo=True)

    def _start_reader(self, port: str, baud: int, demo: bool) -> None:
        """Create and start a DeviceReader thread."""
        if self._reader and self._reader.isRunning():
            return
        self._equilibrium.reset()
        self._reader = DeviceReader(port=port, baud_rate=baud)
        self._reader.set_demo_mode(demo)
        self._reader.measurement_ready.connect(self._on_measurement)
        self._reader.error_occurred.connect(self._on_device_error)
        self._reader.connected.connect(self._on_connected)
        self._reader.disconnected.connect(self._on_disconnected)
        self._reader.start()

    @Slot()
    def _on_disconnect(self) -> None:
        """Stop the device reader."""
        if self._reader:
            self._reader.stop_reading()

    @Slot()
    def _on_export(self) -> None:
        """Show export dialog and save data."""
        if not self._measurements:
            QMessageBox.information(self, self.tr("Export"), self.tr("No data to export."))
            return

        path_str, chosen_filter = QFileDialog.getSaveFileName(
            self,
            self.tr("Export Data"),
            "",
            self.tr(
                "CSV (*.csv);;Excel (*.xlsx);;JSON (*.json);;"
                "Markdown (*.md);;PDF (*.pdf)"
            ),
        )
        if not path_str:
            return

        path = Path(path_str)
        suffix = path.suffix.lower()
        try:
            if suffix == ".csv":
                DataExporter.to_csv(self._measurements, path)
            elif suffix == ".xlsx":
                DataExporter.to_excel(self._measurements, path)
            elif suffix == ".json":
                DataExporter.to_json(self._measurements, path)
            elif suffix == ".md":
                DataExporter.to_markdown(self._measurements, path)
            elif suffix == ".pdf":
                DataExporter.to_pdf(self._measurements, path)
            else:
                QMessageBox.warning(self, self.tr("Export"), self.tr("Unknown file format."))
                return
            QMessageBox.information(
                self,
                self.tr("Export"),
                self.tr("Data saved to:\n%1").replace("%1", str(path)),
            )
        except Exception as exc:  # noqa: BLE001
            logger.exception("Export failed")
            QMessageBox.critical(self, self.tr("Export Error"), str(exc))

    @Slot()
    def _on_clear(self) -> None:
        """Clear all collected measurements."""
        reply = QMessageBox.question(
            self,
            self.tr("Clear Data"),
            self.tr("Delete all recorded measurements?"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._measurements.clear()
            self._equilibrium.reset()
            self._titration.clear_data()
            self._dashboard.reset()

    @Slot()
    def _on_settings(self) -> None:
        """Open the settings dialog."""
        dlg = SettingsDialog(self)
        dlg.exec()

    # ------------------------------------------------------------------
    # Slots — device signals
    # ------------------------------------------------------------------

    @Slot(Measurement)
    def _on_measurement(self, m: Measurement) -> None:
        """Handle a new measurement from the device."""
        result = self._equilibrium.add_reading(m.ph)
        m.equilibrium_reached = result.reached
        self._measurements.append(m)
        self._dashboard.update_measurement(m, result)
        self._titration.add_point(m)
        self._lbl_ph.setText(f"pH {m.ph:.3f}")
        if result.reached:
            self._lbl_eq.setText(self.tr("✓ Equilibrium"))
        else:
            self._lbl_eq.setText("")

    @Slot(str)
    def _on_device_error(self, msg: str) -> None:
        """Show device error in the status bar."""
        self._lbl_status.setText(self.tr("Error: ") + msg)
        logger.error("Device error: %s", msg)

    @Slot()
    def _on_connected(self) -> None:
        """Update UI when device connects."""
        self._lbl_status.setText(self.tr("Connected"))
        self._act_connect.setEnabled(False)
        self._act_disconnect.setEnabled(True)

    @Slot()
    def _on_disconnected(self) -> None:
        """Update UI when device disconnects."""
        self._lbl_status.setText(self.tr("Disconnected"))
        self._act_connect.setEnabled(True)
        self._act_disconnect.setEnabled(False)

    # ------------------------------------------------------------------
    # Window geometry persistence
    # ------------------------------------------------------------------

    def _restore_geometry(self) -> None:
        """Restore saved window position and size."""
        settings = QSettings()
        geo = settings.value("window/geometry")
        if geo:
            self.restoreGeometry(geo)  # type: ignore[arg-type]
        state = settings.value("window/state")
        if state:
            self.restoreState(state)  # type: ignore[arg-type]

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802
        """Save geometry and stop device thread before closing."""
        settings = QSettings()
        settings.setValue("window/geometry", self.saveGeometry())
        settings.setValue("window/state", self.saveState())
        if self._reader and self._reader.isRunning():
            self._reader.stop_reading()
            self._reader.wait(3000)
        super().closeEvent(event)
