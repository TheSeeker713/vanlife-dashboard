"""QApplication bootstrap. Run with: python -m app.main (venv activated).

Theme (dark by default, light on request) is applied inside
MainWindow.__init__ itself, not here, since it depends on the persisted
QSettings value.
"""
from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from app.ui.main_window import MainWindow


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("Vanlife Dashboard")
    app.setOrganizationName("Mycelia Interactive LLC")

    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
