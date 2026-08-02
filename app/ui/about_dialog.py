"""Help > About."""
from __future__ import annotations

from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton

APP_VERSION = "0.1.0-dev"


class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About Vanlife Dashboard")
        self.resize(360, 220)

        layout = QVBoxLayout(self)

        title = QLabel("Vanlife Dashboard")
        title.setObjectName("placeholderTitle")
        layout.addWidget(title)

        body = QLabel(
            f"Version {APP_VERSION}\n\n"
            "A native desktop assistant for organizing raw vanlife\n"
            "documentary footage before post-production in DaVinci\n"
            "Resolve Studio.\n\n"
            "Author: Jeremy Robards, CTO and CAIO\n"
            "Mycelia Interactive LLC"
        )
        body.setWordWrap(True)
        layout.addWidget(body)

        layout.addStretch(1)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
