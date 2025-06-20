import sys

from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QMenu,
    QMenuBar,
    QMessageBox,
    QStatusBar,
    QTabWidget,
)

# Browse tab
from Ward_DND_AI.gui.browse.controller_browse import BrowseController
from Ward_DND_AI.gui.browse.view_browse import BrowseView

# Ask AI tab
from Ward_DND_AI.gui.chat.controller_chat import ChatController
from Ward_DND_AI.gui.chat.view_chat import ChatView

# Create tab (Random Generator)
from Ward_DND_AI.gui.create.controller_create import CreateController
from Ward_DND_AI.gui.create.view_create import CreateView

# New Dashboard tab (stub)
from Ward_DND_AI.gui.dashboard.controller_dashboard import DashboardController
from Ward_DND_AI.gui.dashboard.view_dashboard import DashboardView

# Settings tab
from Ward_DND_AI.gui.settings.controller_settings import SettingsController
from Ward_DND_AI.gui.settings.view_settings import SettingsView

# New World Builder tab
# World tab (Timeline)
from Ward_DND_AI.gui.universe.timeline.controller_timeline import TimelineController
from Ward_DND_AI.gui.universe.timeline.view_timeline import TimelineView


class LoreMainApp(QMainWindow):
    def __init__(self, ai_engine=None, storage_backend=None, config=None):
        super().__init__()
        self.ai = ai_engine
        self.storage = storage_backend
        self._config = config

        self.setWindowTitle("Obsidian Lore Assistant")
        self.resize(1024, 768)

        # --- Central Tab Widget ---
        self.tabview = QTabWidget()
        self.setCentralWidget(self.tabview)

        # --- Add tabs: Dashboard, AI, Browse, Create, World, Settings ---
        self.tabs = {}
        # Dashboard (real view/controller)
        dash_view = DashboardView(self.tabview, self._config)
        self.dashboard_controller = DashboardController(
            dash_view, self.ai, self.storage, self._config
        )
        self.tabview.addTab(dash_view, "Dashboard")
        self.tabs["Dashboard"] = dash_view

        # AI (formerly Ask)
        ai_view = ChatView(self.tabview, self._config)
        self.ask_controller = ChatController(
            ai_view, self.ai, self.storage, self._config
        )
        self.tabview.addTab(ai_view, "AI")
        self.tabs["AI"] = ai_view

        # Browse (formerly Browse Vault)
        browse_view = BrowseView(self.tabview, self._config)
        self.browse_controller = BrowseController(
            browse_view, self.ai, self.storage, self._config
        )
        self.tabview.addTab(browse_view, "Browse")
        self.tabs["Browse"] = browse_view

        # Create (Random Generator)
        # Create (composite)
        create_view = CreateView(self.tabview, self._config)
        self.create_controller = CreateController(
            create_view, self.ai, self.storage, self._config
        )
        self.tabview.addTab(create_view, "Create")
        self.tabs["Create"] = create_view

        # Universe (Timeline)
        universe_view = TimelineView(self.tabview, self._config)
        self.timeline_controller = TimelineController(
            universe_view, self.ai, self.storage, self._config
        )
        self.tabview.addTab(universe_view, "Universe")
        self.tabs["Universe"] = universe_view

        # Settings
        settings_view = SettingsView(self.tabview, self.ai, self._config)
        self.settings_controller = SettingsController(
            settings_view, self._config, self.ai, self.storage
        )
        self.tabview.addTab(settings_view, "Settings")
        self.tabs["Settings"] = settings_view

        # --- Status Bar ---
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        self.statusbar.showMessage("Ready")

        # --- Menu Bar ---
        self._setup_menubar()

        # --- Keyboard Shortcuts ---
        self._setup_shortcuts()

    def _setup_menubar(self):
        from PyQt6.QtGui import QAction, QKeySequence

        menubar = QMenuBar(self)
        filemenu = QMenu("File", self)

        # New Note
        new_action = QAction("New Note", self)
        new_action.setShortcut(QKeySequence("Ctrl+N"))
        new_action.triggered.connect(self._menu_new_note)
        filemenu.addAction(new_action)

        # Import Note
        import_action = QAction("Import Note", self)
        import_action.setShortcut(QKeySequence("Ctrl+I"))
        import_action.triggered.connect(self._menu_import_note)
        filemenu.addAction(import_action)

        # Export Note
        export_action = QAction("Export Note", self)
        export_action.setShortcut(QKeySequence("Ctrl+S"))
        export_action.triggered.connect(self._menu_export_note)
        filemenu.addAction(export_action)

        filemenu.addSeparator()

        # Exit
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        filemenu.addAction(exit_action)

        menubar.addMenu(filemenu)
        self.setMenuBar(menubar)

    def _setup_shortcuts(self):
        # Will wire these to Ask tab after that migration step
        pass

    # --- Menu Actions (Stubbed, to be filled in with tab logic) ---
    def _menu_new_note(self):
        QMessageBox.information(
            self, "Stub", "New Note action (wire to Browse tab later)"
        )

    def _menu_import_note(self):
        QMessageBox.information(
            self, "Stub", "Import Note action (wire to Browse tab later)"
        )

    def _menu_export_note(self):
        QMessageBox.information(
            self, "Stub", "Export Note action (wire to Browse tab later)"
        )


# Standalone run for testing window only (will not break import)
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoreMainApp()
    window.show()
    sys.exit(app.exec())
