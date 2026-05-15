"""Compile all .ts translation files to .qm using PySide6 lrelease.

Usage:
    python scripts/compile_translations.py
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def find_lrelease() -> Path:
    """Locate lrelease(.exe) bundled with PySide6."""
    try:
        import PySide6
    except ImportError:
        print("ERROR: PySide6 is not installed. Run: pip install PySide6", file=sys.stderr)
        sys.exit(1)

    pyside_dir = Path(PySide6.__file__).parent
    # Windows ships lrelease.exe; Linux/macOS ship lrelease
    for name in ("lrelease.exe", "lrelease"):
        candidate = pyside_dir / name
        if candidate.exists():
            return candidate

    print(
        f"ERROR: lrelease not found in {pyside_dir}.\n"
        "Try reinstalling PySide6: pip install --force-reinstall PySide6",
        file=sys.stderr,
    )
    sys.exit(1)


def main() -> None:
    """Compile every .ts file in hi2002app/i18n/ to .qm."""
    lrelease = find_lrelease()
    i18n_dir = Path(__file__).parent.parent / "hi2002app" / "i18n"
    ts_files = sorted(i18n_dir.glob("*.ts"))

    if not ts_files:
        print(f"No .ts files found in {i18n_dir}", file=sys.stderr)
        sys.exit(1)

    print(f"Using lrelease: {lrelease}")
    errors = 0
    for ts in ts_files:
        result = subprocess.run(
            [str(lrelease), str(ts)],
            capture_output=True,
            text=True,
        )
        qm = ts.with_suffix(".qm")
        if result.returncode == 0:
            size = qm.stat().st_size if qm.exists() else 0
            print(f"  OK  {ts.name} -> {qm.name} ({size} bytes)")
        else:
            print(f"  ERR {ts.name}\n{result.stderr}", file=sys.stderr)
            errors += 1

    if errors:
        sys.exit(1)
    print(f"\nDone: {len(ts_files)} file(s) compiled.")


if __name__ == "__main__":
    main()
