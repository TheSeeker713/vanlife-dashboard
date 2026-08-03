"""QApplication bootstrap. Run with: python -m vldash.main (venv activated).

This project's own package is named vldash, not app: it was named app/
originally, but that collided with the sibling SEEKERS_GHOSTS repo's own
app/ package the moment sys.path bridged over to it (see config.py),
since `python -m app.main` caches "app" in sys.modules as this project's
package before any sys.path insert can run. Renamed per the pre-agreed
fallback in INSTRUCTIONS.md Step 2.1.

Theme (light by default, dark on request via the View menu) is applied
inside MainWindow.__init__ itself, not here, since it depends on the
persisted QSettings value.
"""
from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from vldash import db
from vldash.logging_setup import configure_logging
from vldash.ui.main_window import MainWindow


def main() -> int:
    logger = configure_logging()
    logger.info("Starting Vanlife Dashboard")
    db.init_db()

    app = QApplication(sys.argv)
    app.setApplicationName("Vanlife Dashboard")
    app.setOrganizationName("Mycelia Interactive LLC")

    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
