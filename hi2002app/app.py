"""QApplication factory with theme, HiDPI and i18n setup."""

from __future__ import annotations

import sys
import logging
from pathlib import Path

from PySide6.QtCore import QSettings, QTranslator, QLocale, Qt
from PySide6.QtGui import QPalette, QColor
from PySide6.QtWidgets import QApplication

from hi2002app.ui.main_window import MainWindow

log = logging.getLogger(__name__)

APP_NAME = "HI2002App"
ORG_NAME = "HannaInstruments"


def _setup_logging() -> None:
    """Configure file + console logging."""
    import os
    log_dir = Path(os.getenv("LOCALAPPDATA", Path.home())) / APP_NAME / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(log_dir / "app.log", encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )


def _is_dark_theme() -> bool:
    """Detect Windows dark mode via registry."""
    try:
        import winreg
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize",
        )
        value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
        return value == 0
    except Exception:
        return False


def _apply_theme(app: QApplication) -> None:
    """Apply dark or light QSS theme."""
    theme = "dark" if _is_dark_theme() else "light"
    qss_path = Path(__file__).parent / "resources" / "styles" / f"{theme}.qss"
    if qss_path.exists():
        app.setStyleSheet(qss_path.read_text(encoding="utf-8"))
        log.info("Applied theme: %s", theme)
    else:
        log.warning("Theme file not found: %s", qss_path)


def _setup_translator(app: QApplication, lang: str | None = None) -> None:
    """Load Qt translation file for the given language code."""
    settings = QSettings(ORG_NAME, APP_NAME)
    if lang is None:
        lang = settings.value("ui/language", QLocale.system().name()[:2], type=str)
    i18n_dir = Path(__file__).parent / "i18n"
    translator = QTranslator(app)
    qm_file = i18n_dir / f"hi2002app_{lang}.qm"
    if translator.load(str(qm_file)):
        app.installTranslator(translator)
        log.info("Loaded translation: %s", qm_file)
    else:
        log.info("No translation for language '%s', using default (en)", lang)


def run() -> None:
    """Bootstrap and run the application event loop."""
    _setup_logging()

    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setOrganizationName(ORG_NAME)
    app.setApplicationVersion("0.1.0")

    _apply_theme(app)
    _setup_translator(app)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
