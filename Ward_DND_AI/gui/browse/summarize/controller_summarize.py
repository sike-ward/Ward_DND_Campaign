import os

from PyQt6.QtCore import QObject

from Ward_DND_AI.utils.crash_handler import catch_and_report_crashes


class SummarizeController(QObject):
    def __init__(self, view, ai_engine, storage_backend, config, status_var=None):
        super().__init__()
        self.view = view
        self.ai = ai_engine
        self.storage = storage_backend
        self.config = config
        self.status_var = (
            status_var  # Optional status, integrate with your app if needed
        )

        self._load_folders()

        # Connect summarize button with crash handler
        self.view.summarize_btn.clicked.connect(
            catch_and_report_crashes(self.on_summarize)
        )

    def _load_folders(self, *args, **kwargs):
        folders = self.storage.list_folders()
        self.view.folder_menu.clear()
        self.view.folder_menu.addItems(folders)
        if folders:
            self.view.folder_menu.setCurrentIndex(0)

    @catch_and_report_crashes
    def on_summarize(self, *args, **kwargs):
        folder = self.view.folder_menu.currentText().strip()
        style = self.view.style_menu.currentText().strip().lower()

        if not folder:
            self.view.set_output("[No folder selected]")
            if self.status_var:
                self.status_var.setText("❌ No folder selected.")
            return

        notes = self.storage.list_notes(folder)
        if not notes:
            self.view.set_output("[No notes found in folder]")
            if self.status_var:
                self.status_var.setText("⚠️ Folder is empty.")
            return

        try:
            notes_filenames = self.storage.list_notes(folder)
            notes_contents = []
            for filename in notes_filenames:
                full_path = os.path.join(folder, filename)
                content = self.storage.read_note(full_path)
                notes_contents.append(content)

            content = "\n\n".join(notes_contents)

            prompt = f"Summarize the following notes in a {style} format:\n\n{content}"
            summary = self.ai.summarize(prompt)
            if isinstance(summary, tuple):
                summary = summary[0]
            self.view.set_output(summary)

            if self.status_var:
                self.status_var.setText(f"✅ {len(notes)} notes summarized.")
        except Exception as e:
            self.view.set_output(f"[Error: {e}]")
            if self.status_var:
                self.status_var.setText("❌ Summarization failed.")
