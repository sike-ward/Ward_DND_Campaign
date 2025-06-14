import tkinter as tk
import webbrowser


class HelpController:
    def __init__(self, view, ai, storage, config, status_var=None):
        self.v = view
        self.ai = ai
        self.storage = storage
        self.config = config
        self.status_var = status_var or tk.StringVar()
        self._populate()

    def _populate(self):
        help_text = (
            "Welcome to the Obsidian Lore Assistant!\n\n"
            "• Ask AI Tab: Type your question and click 'Ask'.\n"
            "• Browse Vault Tab: Browse and manage your notes.\n"
            "• Summarize Tab: Summarize notes by folder.\n"
            "• Random Generator Tab: Generate random content.\n"
            "• Timeline Tab: Manage your campaign events.\n"
            "• Campaign Settings Tab: Configure your vault path and API key.\n"
            "• Tokens Tab: View session token usage and AI config.\n\n"
            "For full documentation, visit: https://github.com/yourrepo/wiki"
        )
        self.v.set_text(help_text)
        self.status_var.set("✅ Help loaded.")

    def open_docs(self):
        try:
            webbrowser.open("https://github.com/yourrepo/wiki")
            self.status_var.set("📖 Opening documentation in browser...")
        except Exception:
            self.status_var.set("❌ Failed to open documentation.")
