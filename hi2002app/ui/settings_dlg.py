"""Settings dialog for port, language and theme configuration."""

from __future__ import annotations

import logging

import serial.tools.list_ports
from PySide6.QtCore import QSettings
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QGroupBox,
    QLabel,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
)

logger = logging.getLogger(__name__)

_LANGUAGES: dict[str, str] = {
    "English": "en",
    "Русский": "ru",
}

_BAUD_RATES: list[int] = [300, 600, 1200, 2400, 4800, 9600, 19200, 38400, 115200]


class SettingsDialog(QDialog):
    """Modal dialog for application settings.

    Sections:
    - Device: serial port, baud rate.
    - Equilibrium: window size, std threshold, slope threshold.
    - Appearance: language, dark/light theme.
    """

    def __init__(self, parent: QDialog | None = None) -> None:
        """Initialise the settings dialog."""
        super().__init__(parent)
        self.setWindowTitle(self.tr("Settings"))
        self.setMinimumWidth(400)
        self._settings = QSettings()
        self._build_ui()
        self._load_values()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        """Create all form widgets."""
        layout = QVBoxLayout(self)

        # --- Device ---
        dev_box = QGroupBox(self.tr("Device"))
        dev_form = QFormLayout(dev_box)

        self._cb_port = QComboBox()
        self._refresh_ports()
        btn_refresh = QPushButton(self.tr("Refresh"))
        btn_refresh.clicked.connect(self._refresh_ports)
        dev_form.addRow(self.tr("Serial Port:"), self._cb_port)
        dev_form.addRow("", btn_refresh)

        self._cb_baud = QComboBox()
        for b in _BAUD_RATES:
            self._cb_baud.addItem(str(b), b)
        dev_form.addRow(self.tr("Baud Rate:"), self._cb_baud)
        layout.addWidget(dev_box)

        # --- Equilibrium ---
        eq_box = QGroupBox(self.tr("Equilibrium Detection"))
        eq_form = QFormLayout(eq_box)

        self._sp_window = QSpinBox()
        self._sp_window.setRange(3, 100)
        eq_form.addRow(self.tr("Window Size (samples):"), self._sp_window)

        # Use float spinboxes via QDoubleSpinBox workaround
        from PySide6.QtWidgets import QDoubleSpinBox
        self._dsb_std = QDoubleSpinBox()
        self._dsb_std.setRange(0.001, 1.0)
        self._dsb_std.setSingleStep(0.005)
        self._dsb_std.setDecimals(4)
        eq_form.addRow(self.tr("Std Dev Threshold:"), self._dsb_std)

        self._dsb_slope = QDoubleSpinBox()
        self._dsb_slope.setRange(0.0001, 1.0)
        self._dsb_slope.setSingleStep(0.001)
        self._dsb_slope.setDecimals(5)
        eq_form.addRow(self.tr("Slope Threshold:"), self._dsb_slope)
        layout.addWidget(eq_box)

        # --- Appearance ---
        ui_box = QGroupBox(self.tr("Appearance"))
        ui_form = QFormLayout(ui_box)

        self._cb_lang = QComboBox()
        for name, code in _LANGUAGES.items():
            self._cb_lang.addItem(name, code)
        ui_form.addRow(self.tr("Language:"), self._cb_lang)

        self._chk_dark = QCheckBox(self.tr("Dark Theme"))
        ui_form.addRow(self._chk_dark)

        lbl_restart = QLabel(self.tr("* Language and theme changes require a restart."))
        ui_form.addRow(lbl_restart)
        layout.addWidget(ui_box)

        # --- Buttons ---
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._save_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _refresh_ports(self) -> None:
        """Repopulate the serial port combo box."""
        self._cb_port.clear()
        ports = serial.tools.list_ports.comports()
        for p in ports:
            self._cb_port.addItem(f"{p.device} — {p.description}", p.device)
        if self._cb_port.count() == 0:
            self._cb_port.addItem(self.tr("No ports found"), "")

    def _load_values(self) -> None:
        """Load current QSettings values into widgets."""
        port: str = self._settings.value("device/port", "COM1", type=str)  # type: ignore[call-overload]
        idx = self._cb_port.findData(port)
        if idx >= 0:
            self._cb_port.setCurrentIndex(idx)

        baud: int = self._settings.value("device/baud", 1200, type=int)  # type: ignore[call-overload]
        idx = self._cb_baud.findData(baud)
        if idx >= 0:
            self._cb_baud.setCurrentIndex(idx)

        self._sp_window.setValue(
            self._settings.value("equilibrium/window", 10, type=int)  # type: ignore[call-overload]
        )
        self._dsb_std.setValue(
            self._settings.value("equilibrium/std_threshold", 0.02, type=float)  # type: ignore[call-overload]
        )
        self._dsb_slope.setValue(
            self._settings.value("equilibrium/slope_threshold", 0.005, type=float)  # type: ignore[call-overload]
        )

        lang: str = self._settings.value("ui/language", "en", type=str)  # type: ignore[call-overload]
        idx = self._cb_lang.findData(lang)
        if idx >= 0:
            self._cb_lang.setCurrentIndex(idx)

        dark: bool = self._settings.value("ui/dark_mode", False, type=bool)  # type: ignore[call-overload]
        self._chk_dark.setChecked(dark)

    def _save_and_accept(self) -> None:
        """Persist all values and close dialog."""
        self._settings.setValue("device/port", self._cb_port.currentData())
        self._settings.setValue("device/baud", self._cb_baud.currentData())
        self._settings.setValue("equilibrium/window", self._sp_window.value())
        self._settings.setValue("equilibrium/std_threshold", self._dsb_std.value())
        self._settings.setValue("equilibrium/slope_threshold", self._dsb_slope.value())
        self._settings.setValue("ui/language", self._cb_lang.currentData())
        self._settings.setValue("ui/dark_mode", self._chk_dark.isChecked())
        logger.info("Settings saved.")
        QMessageBox.information(
            self,
            self.tr("Settings"),
            self.tr("Settings saved. Restart required for language/theme changes."),
        )
        self.accept()
