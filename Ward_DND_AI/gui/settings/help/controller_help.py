import webbrowser

from PyQt6.QtCore import QObject

from Ward_DND_AI.utils.crash_handler import catch_and_report_crashes


class HelpController(QObject):
    def __init__(self, view, ai, storage, config, status_var=None):
        super().__init__()
        self.v = view
        self.ai = ai
        self.storage = storage
        self.config = config
        self.status_var = status_var or ""

        self._populate()
        self.v.open_docs_clicked.connect(catch_and_report_crashes(self.open_docs))

    @catch_and_report_crashes
    def _populate(self):
        help_text = (
            "Welcome to the Obsidian Lore Assistant!\n\n"
            "• Ask AI Tab: Type your question and click 'Ask'.\n"
            "• Browse Vault Tab: Browse and manage your notes.\n"
            "• Summarize Tab: Summarize notes by folder.\n"
            "• Random Generator Tab: Generate random content.\n"
            "• Timeline Tab: Manage your campaign events.\n"
            "For full documentation, visit: https://github.com/yourrepo/wiki"
        )
        self.v.set_text(help_text)
        self.status_var = "✅ Help loaded."

    @catch_and_report_crashes
    def open_docs(self):
        try:
            webbrowser.open("https://github.com/yourrepo/wiki")
            self.status_var = "📖 Opening documentation in browser..."
        except Exception:
            self.status_var = "❌ Failed to open documentation."
