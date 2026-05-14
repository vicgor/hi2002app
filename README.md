# Hanna HI2002 App

**Desktop application for working with the Hanna Instruments HI2002 pH meter.**  
Built with Python + PySide6, designed for scientists and laboratory staff.

## Features

- 📡 **Real-time pH reading** via serial port (RS-232/USB)
- 📈 **Titration curve** visualization (live plot)
- ⚖️ **Equilibrium detection** — automatic pH stability analysis
- 💾 **Data export**: CSV, Excel, JSON, Markdown, PDF
- 🌍 **Multilingual UI**: English 🇬🇧, Russian 🇷🇺 (extensible via Qt `.ts`/`.qm` files)
- 🌙 **Dark / Light theme** — auto-detected from Windows system settings
- 🖥️ **HiDPI / 4K** support

## Requirements

- Python ≥ 3.11
- PySide6 ≥ 6.7
- See `pyproject.toml` for full dependency list

## Quick Start

```bash
# Clone
git clone https://github.com/vicgor/hi2002app.git
cd hi2002app

# Create venv
python -m venv .venv
.venv\Scripts\activate  # Windows

# Install
pip install -e ".[dev]"

# Run
python -m hi2002app
```

## Project Structure

```
hi2002app/
├── hi2002app/
│   ├── __init__.py
│   ├── __main__.py          # Entry point
│   ├── app.py               # QApplication setup
│   ├── core/
│   │   ├── __init__.py
│   │   ├── device.py        # HI2002 serial communication
│   │   ├── equilibrium.py   # Equilibrium detection algorithm
│   │   └── exporter.py      # CSV/Excel/JSON/MD/PDF export
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── main_window.py   # QMainWindow
│   │   ├── dashboard.py     # Real-time pH widget
│   │   ├── titration.py     # Titration curve widget
│   │   └── settings_dlg.py  # Settings dialog
│   ├── models/
│   │   ├── __init__.py
│   │   └── measurement.py   # Dataclass for measurements
│   ├── i18n/
│   │   ├── hi2002app_en.ts
│   │   └── hi2002app_ru.ts
│   └── resources/
│       ├── styles/
│       │   ├── dark.qss
│       │   └── light.qss
│       └── icons/
│           └── app.ico
├── tests/
│   ├── __init__.py
│   ├── test_device.py
│   ├── test_equilibrium.py
│   └── test_exporter.py
├── .github/
│   └── workflows/
│       ├── ci.yml
│       └── release.yml
├── pyproject.toml
├── CHANGELOG.md
├── .gitignore
└── README.md
```

## License

MIT
