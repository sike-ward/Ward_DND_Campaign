import os
import tkinter as tk
from pathlib import Path
from tkinter import END, messagebox
from tkinter import filedialog as fd

import customtkinter as ctk
import markdown2
from tkhtmlview import HTMLLabel

from Ward_DND_AI.utils.utils import (
    get_all_folders,
    make_title_case_filename,
)


class BrowseController:
    def __init__(self, view, ai, storage, config, status_var=None):
        self.v = view
        self.ai = ai
        self.storage = storage
        self.config = config
        self.status_var = status_var or tk.StringVar()

        self.preview_mode = "text"
        self.original_content = ""
        self._bind_events()
        self.load_folders()
        self.load_notes()

    def _bind_events(self):
        self.v.folder_filter_var.trace("w", lambda *a: self.load_notes())
        self.v.notes_listbox.bind("<<ListboxSelect>>", lambda e: self.preview_note())
        self.v.new_btn.configure(command=self.new_note)
        self.v.import_btn.configure(command=self.import_notes)
        self.v.edit_btn.configure(command=self.enable_edit)
        self.v.save_btn.configure(command=self.save_note)
        self.v.cancel_btn.configure(command=self.cancel_edit)
        self.v.toggle_btn.configure(command=self.toggle_preview)

    def load_folders(self):
        vals = self.storage.list_folders()
        self.v.folder_menu.configure(values=[""] + sorted(vals))

    def load_notes(self):
        folder = self.v.folder_filter_var.get()
        notes = self.storage.list_all_notes(folder)
        self.v.notes_listbox.delete(0, END)
        for n in notes:
            self.v.notes_listbox.insert(END, n)

    def _show_context_menu(self, event):
        menu = tk.Menu(self.v.text_preview, tearoff=0)
        menu.add_command(label="Summarize", command=self.summarize_current)
        menu.add_command(label="Suggest Tags", command=self.tag_current)
        menu.add_command(label="Auto-Link", command=self.link_current)
        menu.tk_popup(event.x_root, event.y_root)

    def summarize_current(self):
        raw = self._get_selected_or_full()
        summary = self.ai.summarize(raw)
        self._insert_output(summary)
        self.status_var.set("Summary added.")

    def tag_current(self):
        raw = self._get_selected_or_full()
        tags = self.ai.suggest_tags(raw)
        self._insert_output("\n\n" + tags)
        self.status_var.set("Tags added.")

    def link_current(self):
        raw = self._get_selected_or_full()
        linked = self.ai.propose_links(raw)
        self._insert_output("\n\n" + linked)
        self.status_var.set("Link suggestions added.")

    def _get_selected_or_full(self):
        try:
            return self.v.text_preview.get("sel.first", "sel.last")
        except tk.TclError:
            return self.v.text_preview.get("1.0", END).strip()

    def _insert_output(self, text):
        self.v.text_preview.configure(state="normal")
        self.v.text_preview.insert(END, f"{text}")
        self.v.text_preview.configure(state="disabled")

    def preview_note(self):
        idx = (self.v.notes_listbox.curselection() or [None])[0]
        sel = None if idx is None else self.v.notes_listbox.get(idx)
        content = ""

        if sel:
            try:
                content = self.storage.read_note(sel)
            except Exception as e:
                content = f"[ERROR: {e}]"

        self.original_content = content

        if self.v.text_preview:
            self.v.text_preview.destroy()
            self.v.text_preview = None
        if self.v.html_preview:
            self.v.html_preview.destroy()
            self.v.html_preview = None

        if self.preview_mode == "html":
            self._show_html(content)
        else:
            self._create_text_preview()
            self.v.text_preview.configure(state="normal")
            self.v.text_preview.delete("1.0", END)
            if sel is None:
                self.status_var.set("No note selected.")
                self.v.text_preview.configure(state="disabled")
                return
            self.v.text_preview.insert("1.0", content)
            self.v.text_preview.configure(state="disabled")
            self.status_var.set(f"Previewing: {sel}")

    def _create_text_preview(self):
        tp = ctk.CTkTextbox(
            self.v.preview_container,
            font=("Consolas", 12),
            state="disabled",
            wrap="word",
            undo=True,
        )
        tp.grid(row=1, column=0, sticky="nsew", padx=6, pady=(0, 4))
        tp.bind("<Button-3>", self._show_context_menu)
        self.v.text_preview = tp

    def _show_html(self, content):
        html = markdown2.markdown(content)
        hp = HTMLLabel(self.v.preview_container, html=html)
        hp.grid(row=1, column=0, sticky="nsew", padx=6, pady=(0, 4))
        self.v.html_preview = hp
        self.status_var.set("HTML view")

    def toggle_preview(self):
        self.preview_mode = "html" if self.preview_mode == "text" else "text"
        self.preview_note()
        self.v.toggle_btn.configure(
            text="Markdown View" if self.preview_mode == "html" else "HTML View"
        )

    def enable_edit(self):
        self.v.text_preview.configure(state="normal")
        self.v.save_btn.configure(state="normal")
        self.v.cancel_btn.configure(state="normal")
        self.v.edit_btn.configure(state="disabled")
        self.status_var.set("Editing…")

    def cancel_edit(self):
        self.v.text_preview.configure(state="normal")
        self.v.text_preview.delete("1.0", END)
        self.v.text_preview.insert("1.0", self.original_content)
        self.v.text_preview.configure(state="disabled")
        self.v.save_btn.configure(state="disabled")
        self.v.cancel_btn.configure(state="disabled")
        self.v.edit_btn.configure(state="normal")
        self.status_var.set("Edit canceled.")

    def save_note(self):
        sel = (self.v.notes_listbox.curselection() or [None])[0]
        if sel is None:
            self.status_var.set("No note selected.")
            return
        new_content = self.v.text_preview.get("1.0", END)
        try:
            self.storage.write_note(sel, new_content)
            self.enable_edit()
            self.status_var.set(f"Saved: {sel}")
        except Exception as e:
            messagebox.showerror("Save failed", str(e))
            self.status_var.set("Save error.")

    def new_note(self):
        dialog = ctk.CTkToplevel(self.v.frame)
        dialog.title("Create New Note")
        dialog.geometry("400x180")

        ctk.CTkLabel(dialog, text="File Name (no .md):").pack(pady=(12, 2))
        entry = ctk.CTkTextbox(dialog, height=28, width=360)
        entry.pack(pady=2)

        ctk.CTkLabel(dialog, text="Select Folder:").pack(pady=(10, 2))
        folder_var = tk.StringVar(dialog)
        folders = get_all_folders(self.config.VAULT_PATH)
        folder_var.set(folders[0] if folders else "")
        ctk.CTkOptionMenu(dialog, variable=folder_var, values=folders, width=360).pack(
            pady=2
        )

        def _create():
            name = entry.get("1.0", "end").strip()
            filename = make_title_case_filename(name)
            if not filename:
                messagebox.showerror("Invalid name", "Please enter a valid file name.")
                return
            rel = (
                f"{folder_var.get()}/{filename}.md"
                if folder_var.get()
                else f"{filename}.md"
            )
            if self.storage.exists(rel):
                messagebox.showerror("Exists", "Note already exists.")
                return
            self.storage.write_note(
                rel,
                "# "
                + filename
                + "\n\n## Notes\n\n- \n\n## Tags\n\n- \n\n## Links\n\n- \n",
            )

            self.v.notes_listbox.insert(END, rel)
            self.v.notes_listbox.selection_clear(0, END)
            self.v.notes_listbox.selection_set(END)

            self.load_notes()
            self.status_var.set(f"Created note: {rel}")
            dialog.destroy()

        btns = ctk.CTkFrame(dialog)
        btns.pack(pady=12)
        ctk.CTkButton(btns, text="Create", command=_create).grid(
            row=0, column=0, padx=6
        )
        ctk.CTkButton(btns, text="Cancel", command=dialog.destroy).grid(
            row=0, column=1, padx=6
        )

    def import_notes(self):
        files = fd.askopenfilenames(
            title="Import Markdown Note(s)",
            filetypes=[("Markdown", "*.md"), ("All Files", "*.*")],
        )
        if not files:
            return
        target = self.v.folder_filter_var.get().strip()
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
        self.status_var.set(f"Imported {count} notes.")

    def export_note(self):
        sel = (self.v.notes_listbox.curselection() or [None])[0]
        if not sel:
            self.status_var.set("No note selected.")
            return
        default = os.path.basename(sel)
        dest = fd.asksaveasfilename(
            title="Export Note", defaultextension=".md", initialfile=default
        )
        if not dest:
            return
        content = self.storage.read_note(sel)
        Path(dest).write_text(content, encoding="utf-8")
        self.status_var.set(f"Exported: {dest}")

    def delete_note(self):
        sel = (self.v.notes_listbox.curselection() or [None])[0]
        if not sel:
            self.status_var.set("No note selected.")
            return
        if not messagebox.askyesno("Delete Note", f"Delete {sel}?"):
            return
        self.storage.delete_note(sel)
        self.load_notes()
        self.status_var.set(f"Deleted: {sel}")

    def open_in_vscode(self):
        sel = (self.v.notes_listbox.curselection() or [None])[0]
        if sel:
            full = os.path.join(self.config.VAULT_PATH, sel)
            os.system(f'code "{full}"')

    def open_in_obsidian(self):
        sel = (self.v.notes_listbox.curselection() or [None])[0]
        if sel:
            vault = os.path.basename(self.config.VAULT_PATH)
            file_encoded = sel.replace("/", "%2F")
            uri = f"obsidian://open?vault={vault}&file={file_encoded}"
            os.system(f'start "" "{uri}"')
