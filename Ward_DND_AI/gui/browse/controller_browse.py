import os
from pathlib import Path

from markdown2 import markdown
from PyQt6.QtWidgets import (
    QMenu,
)

from Ward_DND_AI.utils.crash_handler import catch_and_report_crashes
from Ward_DND_AI.utils.utils import (
    make_title_case_filename,
)


class BrowseController:
    def __init__(self, view, ai, storage, config, status_var=None):
        self.v = view
        self.ai = ai
        self.storage = storage
        self.config = config
        self.status_var = status_var or self.v.status_label

        self.preview_mode = "text"
        self.original_content = ""

        self._bind_events()
        self.load_folders()
        self.load_notes()

    def _bind_events(self):
        self.v.folder_menu.currentTextChanged.connect(
            catch_and_report_crashes(self.load_notes)
        )
        self.v.notes_listbox.itemSelectionChanged.connect(
            catch_and_report_crashes(self.preview_note)
        )
        self.v.new_btn.clicked.connect(catch_and_report_crashes(self.new_note))
        self.v.import_btn.clicked.connect(catch_and_report_crashes(self.import_notes))
        self.v.edit_btn.clicked.connect(catch_and_report_crashes(self.enable_edit))
        self.v.save_btn.clicked.connect(catch_and_report_crashes(self.save_note))
        self.v.cancel_btn.clicked.connect(catch_and_report_crashes(self.cancel_edit))
        self.v.toggle_btn.clicked.connect(catch_and_report_crashes(self.toggle_preview))

    def load_folders(self, *args):
        vals = self.storage.list_folders()
        self.v.clear_folders()
        self.v.add_folders([""] + sorted(vals))

    def load_notes(self, *args):
        folder = self.v.get_current_folder()  # noqa:F841
        notes = self.storage.list_all_notes()
        self.v.clear_notes()
        for n in notes:
            self.v.add_note(n)

    def _show_context_menu(self, pos):
        menu = QMenu(self.v.text_preview)
        menu.addAction("Summarize", catch_and_report_crashes(self.summarize_current))
        menu.addAction("Suggest Tags", catch_and_report_crashes(self.tag_current))
        menu.addAction("Auto-Link", catch_and_report_crashes(self.link_current))
        menu.exec(self.v.text_preview.mapToGlobal(pos))

    def summarize_current(self, *args):
        raw = self._get_selected_or_full()
        if not self.ai:
            self.v.show_status("AI engine not available for summarization.")
            return
        summary = self.ai.summarize(raw)
        self._insert_output(summary)
        self.v.show_status("Summary added.")

    def tag_current(self, *args):
        raw = self._get_selected_or_full()
        if not self.ai:
            self.v.show_status("AI engine not available for tag suggestion.")
            return
        tags = self.ai.suggest_tags(raw)
        self._insert_output("\n\n" + tags)
        self.v.show_status("Tags added.")

    def link_current(self, *args):
        raw = self._get_selected_or_full()
        if not self.ai:
            self.v.show_status("AI engine not available for auto-linking.")
            return
        linked = self.ai.propose_links(raw)
        self._insert_output("\n\n" + linked)
        self.v.show_status("Link suggestions added.")

    def _get_selected_or_full(self):
        if self.v.text_preview is None:
            return ""
        cursor = self.v.text_preview.textCursor()
        if cursor.hasSelection():
            return cursor.selectedText()
        return self.v.text_preview.toPlainText().strip()

    def _insert_output(self, text):
        if self.v.text_preview is None:
            return
        self.v.text_preview.setReadOnly(False)
        self.v.text_preview.append(text)
        self.v.text_preview.setReadOnly(True)

    def preview_note(self, *args):
        sel = self.v.get_selected_note_name()
        content = ""
        if sel:
            try:
                content = self.storage.read_note(sel)
            except Exception as e:
                content = f"[ERROR: {e}]"
        self.original_content = content

        self.v.clear_preview()
        if self.preview_mode == "html":
            self.v.set_preview_mode_html()
            html = markdown(content)
            self.v.set_html_preview(html)
        else:
            self.v.set_preview_mode_text()
            self.v.set_text_preview(content, editable=False)
            if sel is None:
                self.v.show_status("No note selected.")
                self.v.set_text_preview("", editable=True)
                return
            self.v.show_status(f"Previewing: {sel}")

    def toggle_preview(self, *args, **kwargs):
        self.preview_mode = "html" if self.preview_mode == "text" else "text"
        self.preview_note()
        self.v.set_toggle_button_text(
            "Markdown View" if self.preview_mode == "html" else "HTML View"
        )

    def enable_edit(self, *args, **kwargs):
        if self.v.text_preview is not None:
            self.v.set_text_preview(self.original_content, editable=True)
        self.v.enable_buttons(save=True, cancel=True, edit=False)
        self.v.show_status("Editing…")

    def cancel_edit(self, *args, **kwargs):
        if self.v.text_preview is not None:
            self.v.set_text_preview(self.original_content, editable=False)
        self.v.enable_buttons(save=False, cancel=False, edit=True)
        self.v.show_status("Edit canceled.")

    def save_note(self, *args, **kwargs):
        sel = self.v.get_selected_note_name()
        if not sel:
            self.v.show_status("No note selected.")
            return
        if self.v.text_preview is None:
            return
        new_content = self.v.text_preview.toPlainText()
        try:
            self.storage.write_note(sel, new_content)
            self.enable_edit()
            self.v.show_status(f"Saved: {sel}")
        except Exception as e:
            self.v.show_error("Save failed", str(e))
            self.v.show_status("Save error.")

    def new_note(self, *args, **kwargs):
        folder, ok = self.v.ask_user_folder("Select Folder", "Save to folder:")
        if not ok:
            return
        name, ok = self.v.ask_user_filename("File Name", "Enter file name (no .md):")
        if not ok or not name.strip():
            self.v.show_warning("Invalid name", "Please enter a valid file name.")
            return
        filename = make_title_case_filename(name.strip())
        rel = f"{folder}/{filename}.md" if folder else f"{filename}.md"
        if self.storage.exists(rel):
            self.v.show_warning("Exists", "Note already exists.")
            return
        self.storage.write_note(
            rel,
            "# " + filename + "\n\n## Notes\n\n- \n\n## Tags\n\n- \n\n## Links\n\n- \n",
        )
        self.load_notes()
        self.v.show_status(f"Created note: {rel}")

    def import_notes(self, *args, **kwargs):
        files = self.v.ask_user_files(
            "Import Markdown Note(s)", "Markdown (*.md);;All Files (*)"
        )
        if not files:
            return
        target = self.v.get_current_folder().strip()
        count = 0
        for path in files:
            name = Path(path).name
            rel = f"{target}/{name}" if target else name
            content = Path(path).read_text(encoding="utf-8")
            if self.storage.exists(rel):
                continue
            self.storage.write_note(rel, content)
            count += 1
        self.load_notes()
        self.v.show_status(f"Imported {count} notes.")

    def export_note(self, *args, **kwargs):
        sel = self.v.get_selected_note_name()
        if not sel:
            self.v.show_status("No note selected.")
            return
        default = os.path.basename(sel)
        dest = self.v.ask_user_save_path(
            "Export Note", default, "Markdown (*.md);;All Files (*)"
        )
        if not dest:
            return
        content = self.storage.read_note(sel)
        Path(dest).write_text(content, encoding="utf-8")
        self.v.show_status(f"Exported: {dest}")

    def delete_note(self, *args, **kwargs):
        sel = self.v.get_selected_note_name()
        if not sel:
            self.v.show_status("No note selected.")
            return
        if not self.v.ask_user_confirm("Delete Note", f"Delete {sel}?"):
            return
        self.storage.delete_note(sel)
        self.load_notes()
        self.v.show_status(f"Deleted: {sel}")

    def open_in_vscode(self, *args, **kwargs):
        sel = self.v.get_selected_note_name()
        if sel:
            full = os.path.join(self.config.VAULT_PATH, sel)
            self.v.open_external_path(full)

    def open_in_obsidian(self, *args, **kwargs):
        sel = self.v.get_selected_note_name()
        if sel:
            vault = os.path.basename(self.config.VAULT_PATH)
            file_encoded = sel.replace("/", "%2F")
            self.v.open_obsidian_link(vault, file_encoded)
