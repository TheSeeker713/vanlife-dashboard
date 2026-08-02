"""Help > Shortcuts (also bound directly to F1 and '?')."""
from __future__ import annotations

from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QScrollArea, QWidget

# (key, description, live-yet). Keys not yet wired up are shown greyed out
# with a "coming soon" note rather than omitted, since this is meant to be
# a preview of the full transport scheme, not just what already works.
SHORTCUTS: list[tuple[str, str, bool]] = [
    ("F1 / ?", "Open this shortcuts reference", True),
    ("L", "Play forward, repeated presses cycle 1x / 2x / 4x", False),
    ("J", "Play reverse, same speed cycle", False),
    ("K", "Stop, resets shuttle speed", False),
    ("Space", "Play / pause toggle, forward only (timeline/player focus)", False),
    ("Left / Right arrow", "Step one frame while paused", False),
    ("F", "Toggle fullscreen", False),
    ("M", "Drop a marker at the current frame, auto-pauses, opens note editor", False),
    ("1-9", "Instant quick-tag marker (Keeper, B-roll, Reject, ...)", False),
    ("] / [", "Next / previous unreviewed clip", False),
    ("Shift+X", "One-key discard to the Discard folder", False),
]


class ShortcutsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Keyboard Shortcuts")
        self.resize(480, 420)

        outer = QVBoxLayout(self)
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        outer.addWidget(scroll)

        inner = QWidget()
        layout = QVBoxLayout(inner)

        heading = QLabel("Vanlife Dashboard Shortcuts")
        heading.setObjectName("placeholderTitle")
        layout.addWidget(heading)

        for key, desc, live in SHORTCUTS:
            suffix = "" if live else "  (coming soon)"
            row = QLabel(f"<b>{key}</b>: {desc}{suffix}")
            row.setWordWrap(True)
            if not live:
                row.setStyleSheet("color: #6b6864;")
            layout.addWidget(row)

        layout.addStretch(1)
        scroll.setWidget(inner)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        outer.addWidget(close_btn)
