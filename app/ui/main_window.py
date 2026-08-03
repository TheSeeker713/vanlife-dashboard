"""QMainWindow shell: page-bar (Sort/Canvas), drawer-based Sort page layout,
full menu bar roster, theme toggle, layout persistence, Help dialogs.

Redone from the original flat multi-dock Phase 1 attempt, which tested
visually poorly (empty boxy panels, wrong proportions, a tab strip that
landed at the bottom of its group). This version drops QDockWidget
entirely in favor of a fixed-role layout with resizable QSplitters and
collapsible Drawer components, modeled on DaVinci Resolve's page-bar
structure and validated against a click-through HTML mockup before this
file was written.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from PySide6.QtCore import Qt, QSettings
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QToolButton,
    QSplitter,
    QStackedWidget,
    QStatusBar,
)

from .drawer import Drawer
from .shortcuts_dialog import ShortcutsDialog
from .about_dialog import AboutDialog
from .navigate_dialog import NavigateDialog

ORG_NAME = "Mycelia Interactive LLC"
APP_NAME = "VanlifeDashboard"

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
UI_DIR = Path(__file__).resolve().parent


def _placeholder(title: str, body: str) -> QWidget:
    widget = QWidget()
    layout = QVBoxLayout(widget)
    layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

    title_label = QLabel(title)
    title_label.setObjectName("placeholderTitle")
    title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

    body_label = QLabel(body)
    body_label.setObjectName("placeholderLabel")
    body_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    body_label.setWordWrap(True)

    layout.addWidget(title_label)
    layout.addWidget(body_label)
    return widget


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Vanlife Dashboard")
        self.resize(1440, 900)

        self.settings = QSettings(ORG_NAME, APP_NAME)
        self._theme = "dark"

        self._build_central()
        self._build_menu_bar()
        self._build_status_bar()

        self._restore_layout()
        self._apply_theme(self._theme, persist=False)

    # ---- central widget: page-bar + stacked Sort/Canvas pages ------------

    def _build_central(self) -> None:
        central = QWidget()
        outer = QVBoxLayout(central)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        outer.addWidget(self._build_page_bar())

        self.pages = QStackedWidget()
        self.sort_page = self._build_sort_page()
        self.canvas_page = self._build_canvas_page()
        self.pages.addWidget(self.sort_page)
        self.pages.addWidget(self.canvas_page)
        outer.addWidget(self.pages, 1)

        self.setCentralWidget(central)

    def _build_page_bar(self) -> QWidget:
        bar = QWidget()
        bar.setObjectName("pageBar")
        bar.setFixedHeight(40)
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(12, 0, 10, 0)
        layout.setSpacing(4)

        brand = QLabel("Vanlife Dashboard")
        brand.setObjectName("brandLabel")
        layout.addWidget(brand)
        layout.addSpacing(14)

        self._page_tab_buttons: dict[int, QPushButton] = {}
        for index, label in enumerate(("Sort", "Canvas")):
            btn = QPushButton(label)
            btn.setObjectName("pageTab")
            btn.setProperty("active", index == 0)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda _checked=False, i=index: self._switch_page(i))
            layout.addWidget(btn)
            self._page_tab_buttons[index] = btn

        layout.addStretch(1)

        theme_btn = QToolButton()
        theme_btn.setObjectName("iconButton")
        theme_btn.setText("◐")
        theme_btn.setToolTip("Toggle light/dark theme")
        theme_btn.clicked.connect(self._toggle_theme)
        layout.addWidget(theme_btn)

        return bar

    def _switch_page(self, index: int) -> None:
        self.pages.setCurrentIndex(index)
        for i, btn in self._page_tab_buttons.items():
            btn.setProperty("active", i == index)
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    # ---- Sort page: Media Bin | Player+Timeline | Chat/Metadata rail -----

    def _build_sort_page(self) -> QWidget:
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)

        media_bin_content = _placeholder(
            "Media Bin",
            "Pick a clip to get started.\n(Coming in Phase 3.)",
        )
        self.media_bin_drawer = Drawer(
            "Media Bin — Source", media_bin_content, orientation="horizontal", maximizable=True
        )
        self.media_bin_drawer.maximizeToggled.connect(self._on_media_bin_maximize)
        splitter.addWidget(self.media_bin_drawer)

        self.center_column = self._build_center_column()
        splitter.addWidget(self.center_column)

        self.right_rail = self._build_right_rail()
        splitter.addWidget(self.right_rail)

        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setStretchFactor(2, 0)
        splitter.setSizes([300, 800, 300])

        self.sort_splitter = splitter
        return splitter

    def _build_center_column(self) -> QWidget:
        column = QWidget()
        layout = QVBoxLayout(column)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        player = _placeholder(
            "Player",
            "Open a clip from the Media Bin to play it here.\n(Coming in Phase 4.)",
        )
        layout.addWidget(player, 1)

        timeline = _placeholder(
            "Timeline",
            "Markers for the open clip will show up here. (Coming in Phase 5-6.)",
        )
        timeline.setMinimumHeight(56)
        timeline.setMaximumHeight(70)
        layout.addWidget(timeline, 0)

        return column

    def _build_right_rail(self) -> QWidget:
        splitter = QSplitter(Qt.Orientation.Vertical)
        splitter.setChildrenCollapsible(False)

        chat_content = _placeholder(
            "Chat",
            "Tell the agent what to do, like \"file this in Animal clips.\"\n(Coming in Phase 8.)",
        )
        self.chat_drawer = Drawer("Chat", chat_content, orientation="vertical")
        splitter.addWidget(self.chat_drawer)

        metadata_content = _placeholder(
            "Metadata Viewer",
            "Markers, chat notes, and organize history for the open clip.\n(Coming in Phase 6.)",
        )
        self.metadata_drawer = Drawer("Metadata Viewer", metadata_content, orientation="vertical")
        splitter.addWidget(self.metadata_drawer)

        splitter.setSizes([420, 260])
        return splitter

    def _on_media_bin_maximize(self, maximized: bool) -> None:
        self.center_column.setVisible(not maximized)
        self.right_rail.setVisible(not maximized)

    # ---- Canvas page (placeholder, real content in Phase 10) -------------

    def _build_canvas_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        toolbar = QWidget()
        toolbar.setObjectName("drawerHeader")
        toolbar.setFixedHeight(34)
        tb_layout = QHBoxLayout(toolbar)
        tb_layout.setContentsMargins(12, 0, 12, 0)
        board_label = QLabel("Board switcher, boards, and cards land in Phase 10")
        board_label.setObjectName("panelTitle")
        tb_layout.addWidget(board_label)
        tb_layout.addStretch(1)
        layout.addWidget(toolbar)

        content = _placeholder(
            "Canvas",
            "A corkboard for planning bigger edits.\n(Coming in Phase 10.)",
        )
        layout.addWidget(content, 1)

        return page

    # ---- menu bar ---------------------------------------------------------

    def _build_menu_bar(self) -> None:
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu("&File")
        self._add_action(file_menu, "New Canvas Board...", enabled=False)
        self._add_action(file_menu, "Export...", enabled=False)
        self._add_action(file_menu, "Preferences...", enabled=False)
        file_menu.addSeparator()
        exit_action = self._add_action(file_menu, "Exit", shortcut=QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.close)

        edit_menu = menu_bar.addMenu("&Edit")
        self._add_action(edit_menu, "Add Folder...", enabled=False)
        self._add_action(edit_menu, "Undo Marker Edit", shortcut=QKeySequence.StandardKey.Undo, enabled=False)
        self._add_action(edit_menu, "Redo Marker Edit", shortcut=QKeySequence.StandardKey.Redo, enabled=False)
        self._add_action(edit_menu, "Preferences...", enabled=False)

        view_menu = menu_bar.addMenu("&View")
        media_bin_action = self._add_action(view_menu, "Media Bin")
        media_bin_action.setCheckable(True)
        media_bin_action.setChecked(True)
        media_bin_action.toggled.connect(lambda checked: self.media_bin_drawer.set_collapsed(not checked))
        self.media_bin_drawer.collapsedChanged.connect(lambda collapsed: media_bin_action.setChecked(not collapsed))

        chat_action = self._add_action(view_menu, "Chat")
        chat_action.setCheckable(True)
        chat_action.setChecked(True)
        chat_action.toggled.connect(lambda checked: self.chat_drawer.set_collapsed(not checked))
        self.chat_drawer.collapsedChanged.connect(lambda collapsed: chat_action.setChecked(not collapsed))

        metadata_action = self._add_action(view_menu, "Metadata")
        metadata_action.setCheckable(True)
        metadata_action.setChecked(True)
        metadata_action.toggled.connect(lambda checked: self.metadata_drawer.set_collapsed(not checked))
        self.metadata_drawer.collapsedChanged.connect(lambda collapsed: metadata_action.setChecked(not collapsed))

        self._add_action(view_menu, "Resource Monitor", enabled=False)
        view_menu.addSeparator()
        theme_action = self._add_action(view_menu, "Toggle Theme")
        theme_action.triggered.connect(self._toggle_theme)
        reset_layout_action = self._add_action(view_menu, "Reset Layout")
        reset_layout_action.triggered.connect(self._reset_layout)

        clip_menu = menu_bar.addMenu("&Clip")
        self._add_action(clip_menu, "Add Marker", shortcut="M", enabled=False)
        self._add_action(clip_menu, "Organize to...", enabled=False)
        self._add_action(clip_menu, "Discard", shortcut="Shift+X", enabled=False)
        self._add_action(clip_menu, "Transcribe Audio", enabled=False)
        self._add_action(clip_menu, "Re-run Auto-Tag", enabled=False)
        self._add_action(clip_menu, "Next Unreviewed Clip", shortcut="]", enabled=False)
        self._add_action(clip_menu, "Previous Unreviewed Clip", shortcut="[", enabled=False)

        canvas_menu = menu_bar.addMenu("Ca&nvas")
        self._add_action(canvas_menu, "New Board", enabled=False)
        self._add_action(canvas_menu, "Rename Board", enabled=False)
        self._add_action(canvas_menu, "Delete Board", enabled=False)
        self._add_action(canvas_menu, "New Region", enabled=False)

        tools_menu = menu_bar.addMenu("&Tools")
        self._add_action(tools_menu, "Resource Monitor", enabled=False)
        self._add_action(tools_menu, "Model Selection...", enabled=False)
        open_data_action = self._add_action(tools_menu, "Open Data Folder")
        open_data_action.triggered.connect(self._open_data_folder)
        self._add_action(tools_menu, "View Log", enabled=False)

        help_menu = menu_bar.addMenu("&Help")
        shortcuts_action = self._add_action(help_menu, "Shortcuts", shortcut="F1")
        shortcuts_action.triggered.connect(self._show_shortcuts)
        navigate_action = self._add_action(help_menu, "Navigate")
        navigate_action.triggered.connect(self._show_navigate)
        self._add_action(help_menu, "Manual", enabled=False)
        about_action = self._add_action(help_menu, "About")
        about_action.triggered.connect(self._show_about)

        question_mark = QAction(self)
        question_mark.setShortcut(QKeySequence("?"))
        question_mark.triggered.connect(self._show_shortcuts)
        self.addAction(question_mark)

    def _add_action(self, menu, text: str, shortcut=None, enabled: bool = True) -> QAction:
        action = QAction(text, self)
        if shortcut is not None:
            action.setShortcut(shortcut)
        action.setEnabled(enabled)
        menu.addAction(action)
        return action

    # ---- status bar -----------------------------------------------------

    def _build_status_bar(self) -> None:
        status = QStatusBar(self)
        status.showMessage("Ready. Phase 1 scaffolding, no real footage handling yet.")
        self.setStatusBar(status)

    # ---- theme ------------------------------------------------------------

    def _toggle_theme(self) -> None:
        self._apply_theme("light" if self._theme == "dark" else "dark")

    def _apply_theme(self, theme: str, persist: bool = True) -> None:
        self._theme = theme
        qss_path = UI_DIR / f"{theme}_theme.qss"
        app = QApplication.instance()
        if app is not None and qss_path.exists():
            app.setStyleSheet(qss_path.read_text(encoding="utf-8"))
        for btn in getattr(self, "_page_tab_buttons", {}).values():
            btn.style().unpolish(btn)
            btn.style().polish(btn)
        if persist:
            self.settings.setValue("theme", theme)

    # ---- Help actions -------------------------------------------------------

    def _show_shortcuts(self) -> None:
        ShortcutsDialog(self).exec()

    def _show_navigate(self) -> None:
        NavigateDialog(self).exec()

    def _show_about(self) -> None:
        AboutDialog(self).exec()

    def _open_data_folder(self) -> None:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        if sys.platform == "win32":
            os.startfile(DATA_DIR)  # noqa: S606
        else:
            subprocess.Popen(["xdg-open", str(DATA_DIR)])

    # ---- layout persistence ------------------------------------------------

    def _restore_layout(self) -> None:
        geometry = self.settings.value("main_window/geometry")
        if geometry is not None:
            self.restoreGeometry(geometry)

        theme = self.settings.value("theme", "dark")
        self._theme = theme if theme in ("dark", "light") else "dark"

        page_index = int(self.settings.value("current_page", 0))
        self._switch_page(page_index if page_index in (0, 1) else 0)

        if self.settings.value("media_bin/collapsed", False, type=bool):
            self.media_bin_drawer.set_collapsed(True)
        if self.settings.value("media_bin/maximized", False, type=bool):
            self.media_bin_drawer.set_maximized(True)
        if self.settings.value("chat/collapsed", False, type=bool):
            self.chat_drawer.set_collapsed(True)
        if self.settings.value("metadata/collapsed", False, type=bool):
            self.metadata_drawer.set_collapsed(True)

        sort_sizes = self.settings.value("sort_splitter/sizes")
        if sort_sizes:
            self.sort_splitter.setSizes([int(s) for s in sort_sizes])

    def _reset_layout(self) -> None:
        self.media_bin_drawer.set_maximized(False)
        self.media_bin_drawer.set_collapsed(False)
        self.chat_drawer.set_collapsed(False)
        self.metadata_drawer.set_collapsed(False)
        self.sort_splitter.setSizes([300, 800, 300])
        self._switch_page(0)

    def closeEvent(self, event) -> None:  # noqa: N802 (Qt override)
        self.settings.setValue("main_window/geometry", self.saveGeometry())
        self.settings.setValue("theme", self._theme)
        self.settings.setValue("current_page", self.pages.currentIndex())
        self.settings.setValue("media_bin/collapsed", self.media_bin_drawer.is_collapsed())
        self.settings.setValue("media_bin/maximized", self.media_bin_drawer.is_maximized())
        self.settings.setValue("chat/collapsed", self.chat_drawer.is_collapsed())
        self.settings.setValue("metadata/collapsed", self.metadata_drawer.is_collapsed())
        self.settings.setValue("sort_splitter/sizes", self.sort_splitter.sizes())
        super().closeEvent(event)
