"""QApplication factory — theme, HiDPI, translator setup."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

from PySide6.QtCore import QSettings, QTranslator, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from hi2002app.ui.main_window import MainWindow

logger = logging.getLogger(__name__)


def _setup_logging() -> None:
    """Configure file + console logging."""
    log_dir = Path.home() / "AppData" / "Local" / "HI2002App" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "hi2002app.log"

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )


def _detect_dark_mode() -> bool:
    """Detect Windows dark mode from the registry."""
    try:
        import winreg  # type: ignore[import]
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize",
        )
        val, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
        return val == 0
    except Exception:  # noqa: BLE001
        return False


def _load_stylesheet(app: QApplication, dark: bool) -> None:
    """Load QSS stylesheet based on theme."""
    theme = "dark" if dark else "light"
    qss_path = Path(__file__).parent / "resources" / "styles" / f"{theme}.qss"
    if qss_path.exists():
        app.setStyleSheet(qss_path.read_text(encoding="utf-8"))
    else:
        logger.warning("Stylesheet not found: %s", qss_path)


def _install_translator(app: QApplication, locale: str) -> QTranslator:
    """Install Qt translator for *locale* (e.g. 'ru', 'en')."""
    translator = QTranslator(app)
    qm_path = Path(__file__).parent / "i18n" / f"hi2002app_{locale}.qm"
    if qm_path.exists():
        translator.load(str(qm_path))
        app.installTranslator(translator)
        logger.info("Loaded translation: %s", qm_path)
    else:
        logger.warning("Translation file not found: %s", qm_path)
    return translator


def create_app(argv: list[str]) -> QApplication:
    """Create and configure QApplication, return it (caller calls .exec())."""
    _setup_logging()

    # HiDPI
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(argv)
    app.setApplicationName("HI2002App")
    app.setOrganizationName("HannaInstruments")
    app.setApplicationVersion("0.1.0")

    icon_path = Path(__file__).parent / "resources" / "icons" / "app.ico"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    # Theme
    settings = QSettings()
    dark = settings.value("ui/dark_mode", _detect_dark_mode(), type=bool)  # type: ignore[call-overload]
    _load_stylesheet(app, dark)

    # Language
    locale: str = settings.value("ui/language", "en", type=str)  # type: ignore[call-overload]
    _install_translator(app, locale)

    window = MainWindow(dark_mode=dark)
    window.show()

    return app
