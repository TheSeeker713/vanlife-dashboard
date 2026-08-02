"""QMainWindow shell: dockable placeholder panels, full menu bar roster,
layout persistence, and the Help menu dialogs. Phase 1 scaffolding only,
no real panel behavior yet, that lands panel by panel in later phases.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from PySide6.QtCore import Qt, QSettings
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (
    QMainWindow,
    QDockWidget,
    QLabel,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QStatusBar,
    QToolButton,
)

from .shortcuts_dialog import ShortcutsDialog
from .about_dialog import AboutDialog
from .navigate_dialog import NavigateDialog

ORG_NAME = "Mycelia Interactive LLC"
APP_NAME = "VanlifeDashboard"

DATA_DIR = Path(__file__).resolve().parents[2] / "data"


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


EXPAND_GLYPH = "⤢"   # panel not maximized: click to expand
RESTORE_GLYPH = "⤥"  # panel maximized: click to restore siblings


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Vanlife Dashboard")
        self.resize(1440, 900)

        self.settings = QSettings(ORG_NAME, APP_NAME)

        self._docks: dict[str, QDockWidget] = {}
        self._expand_buttons: dict[str, QToolButton] = {}
        self._maximized_dock: str | None = None
        self._pre_maximize_visibility: dict[str, bool] = {}
        self._default_tabs_raised = False

        self._build_central_widget()
        self._build_docks()
        self._build_menu_bar()
        self._build_status_bar()

        self._restore_layout()

    # ---- central widget (Player) --------------------------------------

    def _build_central_widget(self) -> None:
        player = _placeholder(
            "Player",
            "Open a clip from the Browser to play it here.\n(Coming in Phase 4.)",
        )
        self.setCentralWidget(player)

    # ---- dock widgets ---------------------------------------------------

    def _add_dock(
        self,
        key: str,
        title: str,
        body: str,
        area: Qt.DockWidgetArea,
        default_visible: bool = True,
    ) -> QDockWidget:
        dock = QDockWidget(title, self)
        dock.setObjectName(f"dock_{key}")
        dock.setWidget(self._build_panel_content(key, title, body))
        dock.setAllowedAreas(Qt.DockWidgetArea.AllDockWidgetAreas)
        # No native close (X) button: closing a panel that way makes it
        # vanish with no obvious way back (View menu only). Movable and
        # floatable stay on, only "closable" is dropped. Visibility is
        # controlled deliberately, via the View menu toggle or the expand
        # button below, not by an easy-to-fumble title bar click.
        dock.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetMovable
            | QDockWidget.DockWidgetFeature.DockWidgetFloatable
        )
        self.addDockWidget(area, dock)
        dock.setVisible(default_visible)
        self._docks[key] = dock
        return dock

    def _build_panel_content(self, key: str, title: str, body: str) -> QWidget:
        """Placeholder content plus a small header row with an expand/restore
        toggle. Leaves QDockWidget's own native title bar untouched (still
        draggable/floatable/closable as normal), the expand affordance lives
        inside the panel's own content instead so it never risks breaking
        Qt's built-in dock-drag handling."""
        container = QWidget()
        outer = QVBoxLayout(container)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # Fixed height and an explicit background so this row can never be
        # squeezed to nothing by the layout, and is visually unmistakable
        # instead of blending into the panel body.
        header = QWidget()
        header.setFixedHeight(28)
        header.setStyleSheet("background-color: #eae8e4; border-bottom: 1px solid #d8d5d0;")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(6, 2, 6, 2)
        header_layout.addStretch(1)

        expand_btn = QToolButton()
        expand_btn.setText(EXPAND_GLYPH)
        expand_btn.setFixedSize(24, 22)
        expand_btn.setToolTip("Expand this panel, hides the other panels until restored")
        expand_btn.setCheckable(True)
        expand_btn.setAutoRaise(True)
        expand_btn.clicked.connect(lambda: self._toggle_maximize_dock(key))
        header_layout.addWidget(expand_btn)
        self._expand_buttons[key] = expand_btn

        # Explicit stretch factors: header (0) never grows, the placeholder
        # (1) takes all remaining space. Relying on Qt's default stretch
        # distribution here is what let the header drift away from the top
        # in the first place.
        outer.addWidget(header, 0)
        outer.addWidget(_placeholder(title, body), 1)
        return container

    def _toggle_maximize_dock(self, key: str) -> None:
        if self._maximized_dock == key:
            for dock_key, dock in self._docks.items():
                dock.setVisible(self._pre_maximize_visibility.get(dock_key, True))
            self._set_expand_button_state(key, maximized=False)
            self._maximized_dock = None
            return

        if self._maximized_dock is not None:
            self._set_expand_button_state(self._maximized_dock, maximized=False)
        else:
            self._pre_maximize_visibility = {k: d.isVisible() for k, d in self._docks.items()}

        for dock_key, dock in self._docks.items():
            dock.setVisible(dock_key == key)
        self._set_expand_button_state(key, maximized=True)
        self._maximized_dock = key

    def _set_expand_button_state(self, key: str, maximized: bool) -> None:
        button = self._expand_buttons.get(key)
        if button is None:
            return
        button.setChecked(maximized)
        button.setText(RESTORE_GLYPH if maximized else EXPAND_GLYPH)
        button.setToolTip(
            "Restore the other panels" if maximized else "Expand this panel, hides the other panels until restored"
        )

    def _build_docks(self) -> None:
        browser = self._add_dock(
            "browser",
            "Browser",
            "Pick a clip on the left to get started.\n(Coming in Phase 3.)",
            Qt.DockWidgetArea.LeftDockWidgetArea,
        )
        timeline = self._add_dock(
            "timeline",
            "Timeline",
            "Markers for the open clip will show up here.\n(Coming in Phase 5-6.)",
            Qt.DockWidgetArea.BottomDockWidgetArea,
        )
        # Order matters here: whichever of these is added to the shared
        # right-hand dock area LAST ends up as the frontmost tab by default
        # (tabifyDockWidget call order and raise_() both turned out not to
        # control this reliably in testing). Chat is added last on purpose
        # since it's the panel that should be frontmost on first launch.
        canvas = self._add_dock(
            "canvas",
            "Canvas",
            "A corkboard for planning bigger edits.\n(Coming in Phase 10.)",
            Qt.DockWidgetArea.RightDockWidgetArea,
        )
        metadata = self._add_dock(
            "metadata",
            "Metadata Viewer",
            "Markers, chat notes, and organize history for the open clip.\n(Coming in Phase 6.)",
            Qt.DockWidgetArea.RightDockWidgetArea,
        )
        chat = self._add_dock(
            "chat",
            "Chat",
            "Tell the agent what to do, like \"file this in Animal clips.\"\n(Coming in Phase 8.)",
            Qt.DockWidgetArea.RightDockWidgetArea,
        )
        resource_monitor = self._add_dock(
            "resource_monitor",
            "Resource Monitor",
            "Live CPU, RAM, and GPU meters.\n(Coming in the error-handling phase.)",
            Qt.DockWidgetArea.BottomDockWidgetArea,
            default_visible=False,
        )

        # Which tab ends up frontmost is controlled by dock creation order
        # above (see the comment there), not by this call order or by a
        # post-hoc raise_() call, both of which turned out not to stick.
        self.tabifyDockWidget(canvas, metadata)
        self.tabifyDockWidget(canvas, chat)
        self.tabifyDockWidget(timeline, resource_monitor)

    # ---- menu bar ---------------------------------------------------------

    def _build_menu_bar(self) -> None:
        menu_bar = self.menuBar()

        # File
        file_menu = menu_bar.addMenu("&File")
        self._add_action(file_menu, "New Canvas Board...", enabled=False)
        self._add_action(file_menu, "Export...", enabled=False)
        self._add_action(file_menu, "Preferences...", enabled=False)
        file_menu.addSeparator()
        exit_action = self._add_action(file_menu, "Exit", shortcut=QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.close)

        # Edit
        edit_menu = menu_bar.addMenu("&Edit")
        self._add_action(edit_menu, "Add Folder...", enabled=False)
        self._add_action(edit_menu, "Undo Marker Edit", shortcut=QKeySequence.StandardKey.Undo, enabled=False)
        self._add_action(edit_menu, "Redo Marker Edit", shortcut=QKeySequence.StandardKey.Redo, enabled=False)
        self._add_action(edit_menu, "Preferences...", enabled=False)

        # View
        view_menu = menu_bar.addMenu("&View")
        panel_labels = {
            "browser": "Browser",
            "player": None,  # central widget, not a dock
            "timeline": "Timeline",
            "chat": "Chat",
            "canvas": "Canvas",
            "metadata": "Metadata Viewer",
            "resource_monitor": "Resource Monitor",
        }
        for key, dock in self._docks.items():
            action = dock.toggleViewAction()
            action.setText(panel_labels.get(key, dock.windowTitle()))
            view_menu.addAction(action)
        view_menu.addSeparator()
        self._add_action(view_menu, "Theme: Light (default)", enabled=False)
        reset_layout_action = self._add_action(view_menu, "Reset Layout")
        reset_layout_action.triggered.connect(self._reset_layout)

        # Clip
        clip_menu = menu_bar.addMenu("&Clip")
        self._add_action(clip_menu, "Add Marker", shortcut="M", enabled=False)
        self._add_action(clip_menu, "Organize to...", enabled=False)
        self._add_action(clip_menu, "Discard", shortcut="Shift+X", enabled=False)
        self._add_action(clip_menu, "Transcribe Audio", enabled=False)
        self._add_action(clip_menu, "Re-run Auto-Tag", enabled=False)
        self._add_action(clip_menu, "Next Unreviewed Clip", shortcut="]", enabled=False)
        self._add_action(clip_menu, "Previous Unreviewed Clip", shortcut="[", enabled=False)

        # Canvas
        canvas_menu = menu_bar.addMenu("Ca&nvas")
        self._add_action(canvas_menu, "New Board", enabled=False)
        self._add_action(canvas_menu, "Rename Board", enabled=False)
        self._add_action(canvas_menu, "Delete Board", enabled=False)
        self._add_action(canvas_menu, "New Region", enabled=False)

        # Tools
        tools_menu = menu_bar.addMenu("&Tools")
        resource_action = self._docks["resource_monitor"].toggleViewAction()
        resource_action.setText("Resource Monitor")
        tools_menu.addAction(resource_action)
        self._add_action(tools_menu, "Model Selection...", enabled=False)
        open_data_action = self._add_action(tools_menu, "Open Data Folder")
        open_data_action.triggered.connect(self._open_data_folder)
        self._add_action(tools_menu, "View Log", enabled=False)

        # Help
        help_menu = menu_bar.addMenu("&Help")
        shortcuts_action = self._add_action(help_menu, "Shortcuts", shortcut="F1")
        shortcuts_action.triggered.connect(self._show_shortcuts)
        navigate_action = self._add_action(help_menu, "Navigate")
        navigate_action.triggered.connect(self._show_navigate)
        self._add_action(help_menu, "Manual", enabled=False)
        about_action = self._add_action(help_menu, "About")
        about_action.triggered.connect(self._show_about)

        # '?' as a second binding for the shortcuts dialog, alongside F1
        question_mark = QAction(self)
        question_mark.setShortcut(QKeySequence("?"))
        question_mark.triggered.connect(self._show_shortcuts)
        self.addAction(question_mark)

    def _add_action(
        self,
        menu,
        text: str,
        shortcut=None,
        enabled: bool = True,
    ) -> QAction:
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

    # ---- actions ----------------------------------------------------------

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
        state = self.settings.value("main_window/state")
        if geometry is not None:
            self.restoreGeometry(geometry)
        if state is not None:
            self.restoreState(state)

    def _reset_layout(self) -> None:
        self.settings.remove("main_window/geometry")
        self.settings.remove("main_window/state")
        if self._maximized_dock is not None:
            self._set_expand_button_state(self._maximized_dock, maximized=False)
            self._maximized_dock = None
        for dock in self._docks.values():
            dock.setFloating(False)
        self._build_docks_visibility_defaults()

    def _build_docks_visibility_defaults(self) -> None:
        for key, dock in self._docks.items():
            dock.setVisible(key != "resource_monitor")

    def closeEvent(self, event) -> None:  # noqa: N802 (Qt override)
        self.settings.setValue("main_window/geometry", self.saveGeometry())
        self.settings.setValue("main_window/state", self.saveState())
        super().closeEvent(event)

    def showEvent(self, event) -> None:  # noqa: N802 (Qt override)
        super().showEvent(event)
        # tabifyDockWidget's "which tab ends up frontmost" behavior isn't
        # reliably controlled by call order alone (tried that, still landed
        # on the wrong tab), and raise_() is a no-op before the window has
        # actually painted once. Doing it here, guarded to run only once,
        # is the version that actually sticks.
        if not self._default_tabs_raised:
            self._default_tabs_raised = True
            if "chat" in self._docks:
                self._docks["chat"].raise_()
            if "timeline" in self._docks:
                self._docks["timeline"].raise_()
