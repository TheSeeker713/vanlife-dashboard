"""Help > Navigate: a short first-run tour of each panel."""
from __future__ import annotations

from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QScrollArea, QWidget

PANELS: list[tuple[str, str]] = [
    ("Sort / Canvas", "The two pages of this app, switched at the top. Sort is where you triage clips one at a time. Canvas is a big corkboard for planning the edit as a whole."),
    ("Media Bin", "Your raw footage and your sorted output folders, browsable as a thumbnail grid, filmstrip, or list. Pick a clip here to open it in the Player. Collapse it to a drawer or maximize it from its own header."),
    ("Player", "Watch the clip, shuttle through it, drop markers as you go."),
    ("Timeline", "Every marker you've dropped on the open clip, laid out along the clip's length, right under the Player."),
    ("Chat", "Tell the agent what to do in plain language, like 'file this in Animal clips.' It always asks before touching a file."),
    ("Metadata Viewer", "The notes this app has kept on the open clip: your markers, your chat notes, and its own organize history."),
    ("Canvas page", "A corkboard for planning bigger edits, drag clips onto a board and arrange them however the story needs."),
    ("Resource Monitor", "Optional. Live CPU, RAM, and GPU meters, off by default, one click away in the Tools menu if you want them."),
]


class NavigateDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Navigate Vanlife Dashboard")
        self.resize(480, 420)

        outer = QVBoxLayout(self)
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        outer.addWidget(scroll)

        inner = QWidget()
        layout = QVBoxLayout(inner)

        heading = QLabel("What's where")
        heading.setObjectName("placeholderTitle")
        layout.addWidget(heading)

        for name, desc in PANELS:
            row = QLabel(f"<b>{name}</b><br>{desc}")
            row.setWordWrap(True)
            layout.addWidget(row)

        layout.addStretch(1)
        scroll.setWidget(inner)

        close_btn = QPushButton("Got it")
        close_btn.clicked.connect(self.accept)
        outer.addWidget(close_btn)
