# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] — 2026-05-14

### Added
- Initial project scaffold: `pyproject.toml`, `.gitignore`, `README.md`
- Core package: `DeviceReader` (QThread), `EquilibriumDetector`, `DataExporter`, `Measurement` model
- UI package: `MainWindow`, `DashboardWidget`, `TitrationWidget`, `SettingsDialog`
- Real-time pH reading via serial port (Hanna HI2002)
- Titration curve widget with live plotting (pyqtgraph)
- Equilibrium detection: rolling window std + linear regression slope threshold
- Data export: CSV, Excel (.xlsx), JSON, Markdown, PDF (ReportLab)
- Multilingual UI: English and Russian (`QTranslator` + `.qm` files)
- Dark / Light QSS themes with auto-detection from Windows registry
- HiDPI / 4K support (`Qt.HighDpiScaleFactorRoundingPolicy.PassThrough`)
- Window geometry persistence via `QSettings`
- CI pipeline: ruff check + format, mypy strict, pytest via GitHub Actions
- Release workflow: auto-build `.exe` via PyInstaller on `v*.*.*` tag
- Test suite: device parser, equilibrium detector (11 tests incl. NaN/Inf/boundary), data exporter

### Fixed
- Cross-platform log directory (`AppData/Local` on Windows, `~/Library/Logs` on macOS, `~/.local/share` on Linux)
- `QSettings.value()` casts: safe `int(str(...))` / `float(str(...))` pattern to satisfy mypy strict
- `bool` from `QSettings`: `isinstance` check prevents `bool("false") == True` bug
- `winreg` detection isolated to `_platform.py`, excluded from mypy to avoid Linux CI failures
- CI: added `libegl1` system dep and `xvfb-run` for headless PySide6 tests on Ubuntu
- Removed stale `# type: ignore` comments after installing `PySide6-stubs` and `openpyxl` stubs

[0.1.0]: https://github.com/vicgor/hi2002app/releases/tag/v0.1.0
