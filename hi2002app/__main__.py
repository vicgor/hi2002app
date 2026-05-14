"""Entry point for the HI2002 application."""

import sys

from hi2002app.app import create_app


def main() -> None:
    """Start the application."""
    app = create_app(sys.argv)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
