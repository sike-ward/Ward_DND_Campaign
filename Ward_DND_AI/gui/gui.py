import sys

from PyQt6.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QMenu,
    QMenuBar,
    QMessageBox,
    QStatusBar,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from Ward_DND_AI.gui.ask.controller_ask import AskController
from Ward_DND_AI.gui.ask.view_ask import AskView
from Ward_DND_AI.gui.browse.controller_browse import BrowseController
from Ward_DND_AI.gui.browse.view_browse import BrowseView
from Ward_DND_AI.gui.random_generator.controller_random_generator import (
    RandomGeneratorController,
)
from Ward_DND_AI.gui.random_generator.view_random_generator import RandomGeneratorView
from Ward_DND_AI.gui.settings.controller_settings import SettingsController
from Ward_DND_AI.gui.settings.view_settings import SettingsView
from Ward_DND_AI.gui.summarize.controller_summarize import SummarizeController
from Ward_DND_AI.gui.summarize.view_summarize import SummarizeView
from Ward_DND_AI.gui.timeline.controller_timeline import TimelineController
from Ward_DND_AI.gui.timeline.view_timeline import TimelineView


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

        # --- Add tabs (placeholders, real views wired later) ---
        self.tabs = {}
        tab_names = [
            ("Ask AI", "Ask AI Tab Placeholder"),
            ("Browse Vault", "Browse Vault Tab Placeholder"),
            ("Summarize", "Summarize Tab Placeholder"),
            ("Random Generator", "Random Generator Tab Placeholder"),
            ("Timeline", "Timeline Tab Placeholder"),
            ("Settings", "Settings Tab Placeholder"),
        ]
        for tab_id, label in tab_names:
            if tab_id == "Browse Vault":
                browse_view = BrowseView(self.tabview, self._config)
                self.browse_controller = BrowseController(
                    browse_view, self.ai, self.storage, self._config
                )
                self.tabview.addTab(browse_view, tab_id)
                self.tabs[tab_id] = browse_view
            elif tab_id == "Ask AI":
                ask_view = AskView(self.tabview, self._config)
                self.ask_controller = AskController(
                    ask_view, self.ai, self.storage, self._config
                )
                self.tabview.addTab(ask_view, tab_id)
                self.tabs[tab_id] = ask_view
            elif tab_id == "Settings":
                settings_view = SettingsView(self.tabview, self.ai, self._config)
                self.settings_controller = SettingsController(
                    settings_view, self._config, self.ai, self.storage
                )
                self.tabview.addTab(settings_view, tab_id)
                self.tabs[tab_id] = settings_view
            elif tab_id == "Summarize":
                summarize_view = SummarizeView(self.tabview, self._config)
                self.summarize_controller = SummarizeController(
                    summarize_view, self.ai, self.storage, self._config
                )
                self.tabview.addTab(summarize_view, tab_id)
                self.tabs[tab_id] = summarize_view
            elif tab_id == "Random Generator":
                random_gen_view = RandomGeneratorView(self.tabview, self._config)
                self.random_gen_controller = RandomGeneratorController(
                    random_gen_view, self.ai, self.storage, self._config
                )
                self.tabview.addTab(random_gen_view, tab_id)
                self.tabs[tab_id] = random_gen_view
            elif tab_id == "Timeline":
                timeline_view = TimelineView(self.tabview, self._config)
                self.timeline_controller = TimelineController(
                    timeline_view, self.ai, self.storage, self._config
                )
                self.tabview.addTab(timeline_view, tab_id)
                self.tabs[tab_id] = timeline_view
            else:
                w = QWidget()
                layout = QVBoxLayout(w)
                layout.addWidget(QLabel(label))
                self.tabview.addTab(w, tab_id)
                self.tabs[tab_id] = w

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
