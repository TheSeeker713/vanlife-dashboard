"""Reusable collapsible panel used by Media Bin, Chat, and Metadata.

Two orientations: "horizontal" (collapses by shrinking width, used for
Media Bin which sits beside the Player) and "vertical" (collapses by
shrinking height, used for Chat/Metadata which stack in the right rail).
Media Bin additionally gets a maximize toggle; Chat/Metadata don't, that
matches the approved mockup, not every drawer needs every affordance.
"""
from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QToolButton

COLLAPSED_SIZE = 34
EXPAND_GLYPH = "⤢"
RESTORE_GLYPH = "⤥"
COLLAPSE_DOWN_GLYPH = "▾"
COLLAPSE_UP_GLYPH = "▴"
COLLAPSE_LEFT_GLYPH = "◂"
COLLAPSE_RIGHT_GLYPH = "▸"


class Drawer(QWidget):
    collapsedChanged = Signal(bool)
    maximizeToggled = Signal(bool)

    def __init__(
        self,
        title: str,
        content: QWidget,
        orientation: str = "vertical",
        maximizable: bool = False,
        expanded_size: int = 260,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        if orientation not in ("horizontal", "vertical"):
            raise ValueError(f"orientation must be 'horizontal' or 'vertical', got {orientation!r}")
        self._orientation = orientation
        self._maximizable = maximizable
        self._expanded_size = expanded_size
        self._collapsed = False
        self._maximized = False
        self._content = content

        outer_cls = QVBoxLayout if orientation == "vertical" else QVBoxLayout
        outer = outer_cls(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        header = QWidget()
        header.setObjectName("drawerHeader")
        header.setFixedHeight(30)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(10, 0, 4, 0)

        self._title_label = QLabel(title)
        self._title_label.setObjectName("panelTitle")
        header_layout.addWidget(self._title_label)
        header_layout.addStretch(1)

        self._max_btn: QToolButton | None = None
        if maximizable:
            self._max_btn = QToolButton()
            self._max_btn.setText(EXPAND_GLYPH)
            self._max_btn.setToolTip("Maximize this panel")
            self._max_btn.setAutoRaise(True)
            self._max_btn.clicked.connect(self._on_maximize_clicked)
            header_layout.addWidget(self._max_btn)

        self._collapse_btn = QToolButton()
        self._collapse_btn.setAutoRaise(True)
        self._collapse_btn.setToolTip("Collapse")
        self._set_collapse_glyph()
        self._collapse_btn.clicked.connect(self._on_collapse_clicked)
        header_layout.addWidget(self._collapse_btn)

        outer.addWidget(header)
        outer.addWidget(content, 1)

        self._apply_expanded_size()

    # ---- collapse ----------------------------------------------------

    def _on_collapse_clicked(self) -> None:
        self.set_collapsed(not self._collapsed)

    def set_collapsed(self, collapsed: bool) -> None:
        self._collapsed = collapsed
        self._content.setVisible(not collapsed)
        self._title_label.setVisible(not collapsed or self._orientation == "vertical")
        if collapsed:
            self._apply_collapsed_size()
        else:
            self._apply_expanded_size()
        self._set_collapse_glyph()
        self.collapsedChanged.emit(collapsed)

    def is_collapsed(self) -> bool:
        return self._collapsed

    def _set_collapse_glyph(self) -> None:
        if self._orientation == "horizontal":
            self._collapse_btn.setText(COLLAPSE_RIGHT_GLYPH if self._collapsed else COLLAPSE_LEFT_GLYPH)
        else:
            self._collapse_btn.setText(COLLAPSE_UP_GLYPH if self._collapsed else COLLAPSE_DOWN_GLYPH)

    def _apply_collapsed_size(self) -> None:
        if self._orientation == "horizontal":
            self.setMinimumWidth(COLLAPSED_SIZE)
            self.setMaximumWidth(COLLAPSED_SIZE)
        else:
            self.setMinimumHeight(30)
            self.setMaximumHeight(30)

    def _apply_expanded_size(self) -> None:
        if self._orientation == "horizontal":
            self.setMinimumWidth(200)
            self.setMaximumWidth(16777215)
        else:
            self.setMinimumHeight(80)
            self.setMaximumHeight(16777215)

    # ---- maximize (Media Bin only) -------------------------------------

    def _on_maximize_clicked(self) -> None:
        self.set_maximized(not self._maximized)

    def set_maximized(self, maximized: bool) -> None:
        if not self._maximizable:
            return
        self._maximized = maximized
        if self._max_btn is not None:
            self._max_btn.setText(RESTORE_GLYPH if maximized else EXPAND_GLYPH)
            self._max_btn.setToolTip("Restore the other panels" if maximized else "Maximize this panel")
        if maximized and self._collapsed:
            self.set_collapsed(False)
        self.maximizeToggled.emit(maximized)

    def is_maximized(self) -> bool:
        return self._maximized
