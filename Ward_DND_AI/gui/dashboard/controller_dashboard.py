import os

from PyQt6.QtCore import QObject


class DashboardController(QObject):
    def __init__(self, view, ai_engine, storage_backend, config, status_var=None):
        super().__init__()
        self.view = view
        self.ai_engine = ai_engine
        self.storage = storage_backend
        self.config = config

        self._bind_events()
        self.refresh()

    # ── Event binding ──────────────────────────────────────────────────
    def _bind_events(self):
        self.view.btn_refresh.clicked.connect(self.refresh)
        self.view.btn_new_note.clicked.connect(self._on_new_note)
        self.view.btn_browse.clicked.connect(self._on_browse)
        self.view.btn_ask_ai.clicked.connect(self._on_ask_ai)
        self.view.recent_list.itemDoubleClicked.connect(self._on_open_recent)

    # ── Refresh / stats ────────────────────────────────────────────────
    def refresh(self):
        vault_path = getattr(self.config, "VAULT_PATH", "")
        if not vault_path or not os.path.isdir(vault_path):
            self.view.status_label.setText(f"Vault not found: {vault_path}")
            return

        notes = self._count_files(vault_path, ".md")
        folders = self._count_dirs(vault_path)
        characters = self._count_dnd_meta(vault_path, "characters")
        sessions = self._count_dnd_meta(vault_path, "sessions")

        self.view.set_stat(self.view.stat_notes, str(notes))
        self.view.set_stat(self.view.stat_folders, str(folders))
        self.view.set_stat(self.view.stat_characters, str(characters))
        self.view.set_stat(self.view.stat_sessions, str(sessions))

        self._load_recent_notes(vault_path)
        self.view.status_label.setText("Dashboard refreshed.")

    def _count_files(self, path: str, ext: str) -> int:
        count = 0
        for root, dirs, files in os.walk(path):
            dirs[:] = [d for d in dirs if not d.startswith(".")]
            count += sum(1 for f in files if f.endswith(ext))
        return count

    def _count_dirs(self, path: str) -> int:
        count = 0
        for root, dirs, files in os.walk(path):
            dirs[:] = [d for d in dirs if not d.startswith(".")]
            count += len(dirs)
        return count

    def _count_dnd_meta(self, vault_path: str, subfolder: str) -> int:
        meta_dir = os.path.join(vault_path, ".dnd_meta", subfolder)
        if not os.path.isdir(meta_dir):
            return 0
        return sum(1 for f in os.listdir(meta_dir) if f.endswith(".json"))

    def _load_recent_notes(self, vault_path: str, max_notes: int = 10):
        notes = []
        for root, dirs, files in os.walk(vault_path):
            dirs[:] = [d for d in dirs if not d.startswith(".")]
            for f in files:
                if f.endswith(".md"):
                    full = os.path.join(root, f)
                    notes.append((os.path.getmtime(full), full))

        notes.sort(reverse=True)
        self.view.recent_list.clear()
        for _, path in notes[:max_notes]:
            rel = os.path.relpath(path, vault_path)
            self.view.recent_list.addItem(rel)

    # ── Button handlers ────────────────────────────────────────────────
    def _on_new_note(self):
        # Switch to Browse tab and trigger new-note flow
        main_window = self.view.window()
        if hasattr(main_window, "tabview"):
            main_window.tabview.setCurrentWidget(main_window.tabs.get("Browse", self.view))
        if hasattr(main_window, "browse_controller"):
            main_window.browse_controller.new_note()

    def _on_browse(self):
        main_window = self.view.window()
        if hasattr(main_window, "tabview"):
            main_window.tabview.setCurrentWidget(main_window.tabs.get("Browse", self.view))

    def _on_ask_ai(self):
        main_window = self.view.window()
        if hasattr(main_window, "tabview"):
            main_window.tabview.setCurrentWidget(main_window.tabs.get("AI", self.view))

    def _on_open_recent(self, item):
        """Open a double-clicked recent note in the Browse tab."""
        rel_path = item.text()
        main_window = self.view.window()
        if hasattr(main_window, "tabview"):
            main_window.tabview.setCurrentWidget(main_window.tabs.get("Browse", self.view))
        if hasattr(main_window, "browse_controller"):
            main_window.browse_controller.open_note_by_path(rel_path)
