import tkinter as tk


class SummarizeController:
    def __init__(self, view, ai, storage, config, status_var=None):
        self.view = view
        self.ai = ai
        self.storage = storage
        self.config = config
        self.status_var = status_var or tk.StringVar()

        self.view.summarize_btn.configure(command=self.on_summarize)

        folders = self.storage.get_all_folders()
        self.view.folder_menu.configure(values=folders)
        if folders:
            self.view.folder_menu.set(folders[0])

    def on_summarize(self):
        folder = self.view.folder_menu.get().strip()
        style = self.view.style_menu.get().strip().lower()

        if not folder:
            self._show_output("[No folder selected]")
            self.status_var.set("❌ No folder selected.")
            return

        notes = self.storage.get_notes_in_folder(folder)
        if not notes:
            self._show_output("[No notes found in folder]")
            self.status_var.set("⚠️ Folder is empty.")
            return

        try:
            content = "\n\n".join(n.body for n in notes)
            prompt = f"Summarize the following notes in a {style} format:\n\n{content}"
            summary = self.ai.summarize(prompt)
            self._show_output(summary)
            self.status_var.set(f"✅ {len(notes)} notes summarized.")
        except Exception as e:
            self._show_output(f"[Error: {e}]")
            self.status_var.set("❌ Summarization failed.")

    def _show_output(self, text):
        self.view.output_text.configure(state="normal")
        self.view.output_text.delete("1.0", "end")
        self.view.output_text.insert("1.0", text)
        self.view.output_text.configure(state="disabled")
