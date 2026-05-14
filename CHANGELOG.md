# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial project scaffold
- Real-time pH reading via serial port (HI2002)
- Titration curve widget with live plotting (pyqtgraph)
- Equilibrium detection algorithm (rolling window + slope threshold)
- Data export: CSV, Excel (.xlsx), JSON, Markdown, PDF (ReportLab)
- Multilingual UI: English and Russian (Qt Translator)
- Dark / Light theme auto-detection from Windows system settings
- HiDPI / 4K support
- CI pipeline (ruff, mypy, pytest) via GitHub Actions
- Auto-build `.exe` via PyInstaller on `v*.*.*` tag

