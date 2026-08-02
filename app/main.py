"""QApplication bootstrap. Run with: python -m app.main (venv activated)."""
from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from app.ui.main_window import MainWindow

THEME_PATH = Path(__file__).resolve().parent / "ui" / "theme.qss"


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("Vanlife Dashboard")
    app.setOrganizationName("Mycelia Interactive LLC")

    if THEME_PATH.exists():
        app.setStyleSheet(THEME_PATH.read_text(encoding="utf-8"))

    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
