"""Platform-specific helpers (Windows registry, etc.).

This module is excluded from mypy checking because ``winreg`` is only
available on Windows and has no cross-platform stubs.
"""

from __future__ import annotations

import platform


def detect_dark_mode() -> bool:
    """Detect Windows dark mode via the registry. Returns False on non-Windows."""
    if platform.system() != "Windows":
        return False
    try:
        import winreg

        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize",
        )
        val, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
        return val == 0
    except Exception:  # noqa: BLE001
        return False
