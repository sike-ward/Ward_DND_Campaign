import datetime
import os
import platform
import re
import tempfile
import tkinter as tk
import tkinter.filedialog as fd
import urllib.parse
import webbrowser
from tkinter import END, messagebox

import customtkinter as ctk
import markdown2
from tkhtmlview import HTMLLabel

from Ward_DND_AI.ai.ai_engine import LoreAI, count_tokens
from Ward_DND_AI.config.config import Config, log_exception
from Ward_DND_AI.gui.tooltip import ToolTip
from Ward_DND_AI.utils.utils import (
    auto_link_notes,
    get_all_folders,
    get_note_names,
    highlight_markdown,
    make_title_case_filename,
)


class LoreMainApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        self.title("Obsidian Lore Assistant")
        self.geometry("1050x900")

        self._setup_menubar()

        self.config = Config()
        self.ai = LoreAI(self.config.VAULT_PATH)
        self.last_answer = ""
        self.history = []

        self.status_var = tk.StringVar()
        self.status_var.set("Ready.")

        self.session_tokens = 0
        self.token_limit = 5000  # Per-request warning threshold

        self.tabview = ctk.CTkTabview(self, width=1020, height=830)
        self.tabview.pack(padx=8, pady=8, fill="both", expand=True)

        self._setup_ask_tab()
        self._setup_browse_tab()
        self._setup_summarize_tab()
        self._setup_random_generator_tab()
        self._setup_timeline_tab()
        self._setup_campaign_settings_tab()
        self._setup_help_tab()
        self._setup_token_tab()

        self.bind("<Control-s>", lambda e: self.save_note())
        self.bind("<Control-Return>", lambda e: self.ask_question())
        self.bind("<F1>", lambda e: self.tabview.set("Help / About"))
        self.bind(
            "<Control-p>",
            lambda e: self.preview_in_browser(self.output_box.get("1.0", "end")),
        )
        self.bind("<Control-Shift-S>", lambda e: self.browse_export_note())
        self.bind("<Control-i>", lambda e: self.browse_import_note())
        self.bind("<Control-Tab>", self.next_tab)
        self.bind("<Control-Shift-Tab>", self.prev_tab)

        self.status_label = ctk.CTkLabel(
            self, textvariable=self.status_var, font=("Segoe UI", 18, "bold")
        )
        self.status_label.pack(side="bottom", pady=(6, 8))
        self.browse_original_content = ""
        self.browse_html_preview = None
        self.browse_preview_mode = "text"

    def _setup_menubar(self):
        menubar = tk.Menu(self)

        # --- File Menu ---
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(
            label="Save Note", command=self.save_note, accelerator="Ctrl+S"
        )
        filemenu.add_command(
            label="Export Note",
            command=self.browse_export_note,
            accelerator="Ctrl+Shift+S",
        )
        filemenu.add_command(
            label="Import Note", command=self.browse_import_note, accelerator="Ctrl+I"
        )
        filemenu.add_separator()
        filemenu.add_command(
            label="Ask AI", command=self.ask_question, accelerator="Ctrl+Enter"
        )
        filemenu.add_command(
            label="Preview",
            command=lambda: self.preview_in_browser(self.output_box.get("1.0", "end")),
            accelerator="Ctrl+P",
        )
        filemenu.add_command(
            label="Next Tab", command=self.next_tab, accelerator="Ctrl+Tab"
        )
        filemenu.add_command(
            label="Previous Tab", command=self.prev_tab, accelerator="Ctrl+Shift+Tab"
        )
        filemenu.add_command(
            label="Show Help/About",
            command=lambda: self.tabview.set("Help / About"),
            accelerator="F1",
        )
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.quit)
        menubar.add_cascade(label="File", menu=filemenu)

        # --- Edit Menu ---
        editmenu = tk.Menu(menubar, tearoff=0)
        editmenu.add_command(
            label="Undo", command=lambda: self.try_undo(), accelerator="Ctrl+Z"
        )
        editmenu.add_command(
            label="Redo", command=lambda: self.try_redo(), accelerator="Ctrl+Y"
        )
        editmenu.add_separator()
        editmenu.add_command(
            label="Cut",
            command=lambda: self.focus_get().event_generate("<<Cut>>"),
            accelerator="Ctrl+X",
        )
        editmenu.add_command(
            label="Copy",
            command=lambda: self.focus_get().event_generate("<<Copy>>"),
            accelerator="Ctrl+C",
        )
        editmenu.add_command(
            label="Paste",
            command=lambda: self.focus_get().event_generate("<<Paste>>"),
            accelerator="Ctrl+V",
        )
        editmenu.add_separator()
        editmenu.add_command(label="Find", command=self.find_text, accelerator="Ctrl+F")
        editmenu.add_command(
            label="Replace", command=self.replace_text, accelerator="Ctrl+H"
        )
        menubar.add_cascade(label="Edit", menu=editmenu)

        # --- AI Menu ---
        aimenu = tk.Menu(menubar, tearoff=0)
        aimenu.add_command(
            label="Ask", command=self.ask_question, accelerator="Ctrl+Enter"
        )
        aimenu.add_command(label="Summarize Folder", command=self.summarize_folder)
        aimenu.add_command(label="Tokens", command=lambda: self.tabview.set("Tokens"))
        # Add more AI helpers as you build them
        menubar.add_cascade(label="AI", menu=aimenu)

        self.config(menu=menubar)

    def _setup_ask_tab(self):
        tab = self.tabview.add("Ask AI")
        tab.rowconfigure(0, weight=1)
        tab.columnconfigure(0, weight=1)

        main = ctk.CTkFrame(tab)
        main.grid(row=0, column=0, sticky="nsew", padx=12, pady=12)
        main.rowconfigure(0, weight=0)
        main.rowconfigure(1, weight=0)
        main.rowconfigure(2, weight=0)
        main.rowconfigure(3, weight=1)
        main.rowconfigure(4, weight=1)
        main.columnconfigure(0, weight=1)

        ctk.CTkLabel(main, text="Ask about your world:", font=("Segoe UI", 15)).grid(
            row=0, column=0, sticky="w", padx=6, pady=(8, 2)
        )
        self.input_box = ctk.CTkTextbox(
            main, height=44, font=("Consolas", 14), undo=True
        )
        # place the prompt textbox
        self.input_box.grid(row=1, column=0, sticky="nsew", padx=6, pady=(0, 4))

        self.output_box = ctk.CTkTextbox(
            main, font=("Consolas", 13), wrap="word", state="disabled", undo=True
        )

        self.input_box.bind("<Control-Return>", lambda e: self.ask_question())
        self.input_box.bind("<Control-s>", lambda e: self.save_note())
        self.input_box.bind(
            "<<Modified>>", lambda e: self.highlight_markdown(self.input_box)
        )

        btns = ctk.CTkFrame(main)
        btns.grid(row=2, column=0, sticky="ew", padx=6, pady=(0, 10))
        btns.columnconfigure((0, 1, 2, 3, 4), weight=1)

        btn_ask = ctk.CTkButton(btns, text="Ask", command=self.ask_question, height=36)
        btn_ask.grid(row=0, column=0, padx=2, pady=2, sticky="ew")
        ToolTip(btn_ask, "Ask a question about your world (Ctrl+Enter also works)")

        btn_save = ctk.CTkButton(btns, text="Save", command=self.save_note, height=36)
        btn_save.grid(row=0, column=1, padx=2, pady=2, sticky="ew")
        ToolTip(btn_save, "Save the current AI response as a Markdown note")

        btn_split = ctk.CTkButton(
            btns, text="Split & Save", command=self.split_and_save_multiple, height=36
        )
        btn_split.grid(row=0, column=2, padx=2, pady=2, sticky="ew")
        ToolTip(
            btn_split, "Split the response into multiple notes (if multiple headings)"
        )

        self.save_note_btn = btn_save
        self.split_note_btn = btn_split
        self.save_note_btn.configure(state="disabled")
        self.split_note_btn.configure(state="disabled")

        btn_preview = ctk.CTkButton(
            btns,
            text="Preview",
            command=lambda: self.preview_in_browser(
                auto_link_notes(
                    self.output_box.get("1.0", END),
                    get_note_names(self.config.VAULT_PATH),
                )
            ),
            height=36,
        )
        btn_preview.grid(row=0, column=3, padx=2, pady=2, sticky="ew")
        ToolTip(btn_preview, "Preview the Markdown output in your browser")

        btn_clear = ctk.CTkButton(
            btns, text="Clear History", command=self.clear_history, height=36
        )
        btn_clear.grid(row=0, column=4, padx=2, pady=2, sticky="ew")
        ToolTip(btn_clear, "Clear the conversation history for this session")

        ctk.CTkLabel(
            main, text="AI Response / Note Preview:", font=("Segoe UI", 13, "italic")
        ).grid(row=3, column=0, sticky="w", padx=6, pady=(0, 3))
        self.output_box = ctk.CTkTextbox(
            main, font=("Consolas", 13), wrap="word", state="disabled"
        )
        self.output_box.grid(row=3, column=0, sticky="nsew", padx=6, pady=(0, 10))

        ctk.CTkLabel(main, text="Conversation History:", font=("Segoe UI", 13)).grid(
            row=4, column=0, sticky="w", padx=6, pady=(0, 2)
        )
        history_frame = ctk.CTkFrame(main)
        history_frame.grid(row=4, column=0, sticky="nsew", padx=6, pady=(0, 8))
        history_frame.rowconfigure(0, weight=1)
        history_frame.columnconfigure(0, weight=1)
        self.history_text = ctk.CTkTextbox(
            history_frame, font=("Consolas", 11), wrap="word", state="disabled"
        )
        self.history_text.grid(row=0, column=0, sticky="nsew")
        scrollbar = ctk.CTkScrollbar(history_frame, command=self.history_text.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.history_text.configure(yscrollcommand=scrollbar.set)

    # ---- BROWSE TAB and all methods below ----

    def _setup_browse_tab(self):
        # ensure notes & tags are loaded before building the filters
        self._browse_load_notes()

        tab = self.tabview.add("Browse Vault")
        tab.rowconfigure(0, weight=1)
        tab.columnconfigure(0, weight=1)
        tab.columnconfigure(1, weight=5)

        main = ctk.CTkFrame(tab)
        main.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=12, pady=12)
        main.rowconfigure(0, weight=1)
        main.columnconfigure(0, weight=1)
        main.columnconfigure(1, weight=3)

        # --- Left Pane ---
        left = ctk.CTkFrame(main)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=0)
        left.rowconfigure(2, weight=1)  # notes list now on row 2
        left.columnconfigure((0, 1, 2), weight=0)
        left.columnconfigure((3, 4), weight=1)

        # Folder filter + Search
        self.folder_filter_var = tk.StringVar()
        folders = get_all_folders(self.config.VAULT_PATH)
        self.folder_filter_var.set("")
        ctk.CTkLabel(left, text="Folder:", font=("Segoe UI", 13)).grid(
            row=0, column=0, sticky="w", padx=(6, 2), pady=(6, 2)
        )
        ctk.CTkOptionMenu(
            left, variable=self.folder_filter_var, values=folders, width=160
        ).grid(row=0, column=1, sticky="ew", padx=(2, 8), pady=(6, 2))
        self.folder_filter_var.trace_add(
            "write", lambda *a: self._browse_filter_notes()
        )

        ctk.CTkLabel(left, text="Search:", font=("Segoe UI", 13)).grid(
            row=0, column=2, sticky="e", padx=(8, 2), pady=(6, 2)
        )
        self.browse_search_var = tk.StringVar()
        ctk.CTkEntry(left, textvariable=self.browse_search_var).grid(
            row=0, column=3, sticky="ew", padx=(2, 6), pady=(6, 2)
        )

        # — define the Tag filter variable —
        self.tag_filter_var = tk.StringVar(value="")

        # — Tag filter dropdown (now its own row) —
        ctk.CTkLabel(left, text="Tag:", font=("Segoe UI", 13)).grid(
            row=1, column=0, sticky="w", padx=(6, 2), pady=(0, 2)
        )
        self.tag_filter_menu = ctk.CTkOptionMenu(
            left,
            variable=self.tag_filter_var,
            values=[""] + sorted(self.all_tags),
            width=120,
            fg_color="#44475a",
            text_color="#f8f8f2",
            button_color="#6272a4",
        )
        self.tag_filter_menu.grid(row=1, column=1, sticky="w", padx=(2, 8), pady=(0, 2))
        self.tag_filter_var.trace_add("write", lambda *a: self._browse_filter_notes())

        # Notes list (row 2)
        self.browse_listbox = tk.Listbox(
            left,
            font=("Consolas", 12),
            selectmode="extended",
            exportselection=False,
            activestyle="dotbox",
        )
        self.browse_listbox.grid(
            row=2, column=0, columnspan=4, sticky="nsew", padx=6, pady=(0, 8)
        )
        scroll = ctk.CTkScrollbar(
            left, orientation="vertical", command=self.browse_listbox.yview
        )
        scroll.grid(row=2, column=4, sticky="ns", pady=(0, 8))
        self.browse_listbox.configure(yscrollcommand=scroll.set)
        self.browse_listbox.bind(
            "<<ListboxSelect>>", lambda e: self.browse_preview_note()
        )

        # Left-pane action buttons (row 3+)
        btns = ctk.CTkFrame(left)
        btns.grid(row=3, column=0, columnspan=4, sticky="ew", padx=6, pady=(0, 8))
        btns.columnconfigure((0, 1), weight=1)
        ctk.CTkButton(
            btns, text="Open in VS Code", command=self.browse_open_in_vscode, height=36
        ).grid(row=0, column=0, padx=2, pady=2, sticky="ew")
        ctk.CTkButton(
            btns,
            text="Open in Obsidian",
            command=self.browse_open_in_obsidian,
            height=36,
        ).grid(row=0, column=1, padx=2, pady=2, sticky="ew")

        ctk.CTkButton(left, text="New Note", command=self.browse_new_note).grid(
            row=4, column=0, columnspan=4, sticky="ew", padx=6, pady=(0, 8)
        )
        ctk.CTkButton(left, text="AI Summarize", command=self.browse_ai_summarize).grid(
            row=5, column=0, columnspan=4, sticky="ew", padx=6, pady=(0, 8)
        )

        # --- Right Pane ---
        right = ctk.CTkFrame(main)
        self.browse_preview_container = right
        right.grid(row=0, column=1, sticky="nsew", padx=(0, 0), pady=0)
        for r in range(7):
            right.rowconfigure(r, weight=(1 if r == 1 else 0))
        right.columnconfigure(0, weight=1)
        right.columnconfigure(1, weight=0)

        # START: Markdown preview → CTkTextbox patch
        # Preview label + Markdown editor with live highlighting
        ctk.CTkLabel(right, text="Preview:", font=("Segoe UI", 13)).grid(
            row=0, column=0, sticky="w", padx=6, pady=(6, 2)
        )
        # — Persistent HTML preview (hidden initially) —
        self.browse_html_preview = HTMLLabel(
            right,
            html="",  # nothing to show yet
            background="#23272e",
            foreground="#ECECEC",
        )
        self.browse_html_preview.grid(
            row=1, column=0, columnspan=2, sticky="nsew", padx=6, pady=(0, 4)
        )
        self.browse_html_preview.grid_remove()

        self.browse_preview_box = ctk.CTkTextbox(
            right, font=("Consolas", 12), wrap="word", undo=True
        )
        self.browse_preview_box.grid(
            row=1, column=0, columnspan=2, sticky="nsew", padx=6, pady=(0, 4)
        )
        # bind your util’s highlighter on every edit
        self.browse_preview_box.bind(
            "<<Modified>>", lambda e: highlight_markdown(self.browse_preview_box)
        )
        self.browse_preview_box.configure(state="disabled")
        # END: Markdown preview → CTkTextbox patch

        # — Persistent HTML preview (hidden initially) —
        self.browse_preview_mode = "text"
        self.browse_html_preview = HTMLLabel(
            right, html="", background="#23272e", foreground="#ECECEC"  # empty at start
        )
        self.browse_html_preview.grid(
            row=1, column=0, columnspan=2, sticky="nsew", padx=6, pady=(0, 4)
        )
        self.browse_html_preview.grid_remove()

        # — Toggle between raw ↔ formatted —
        self.preview_toggle_btn = ctk.CTkButton(
            right,
            text="HTML View",
            command=self.toggle_browse_preview,
            width=100,
            height=32,
        )
        self.preview_toggle_btn.grid(
            row=2, column=1, sticky="e", padx=(0, 12), pady=(0, 4)
        )

        # Edit / Save / Cancel
        self.edit_note_btn = ctk.CTkButton(
            right, text="Edit", command=self.enable_browse_edit
        )
        self.edit_note_btn.grid(row=3, column=0, sticky="w", padx=6, pady=(0, 2))
        self.save_note_btn = ctk.CTkButton(
            right, text="Save Changes", command=self.browse_save_note
        )
        self.save_note_btn.grid(row=4, column=0, sticky="e", padx=6, pady=(0, 2))
        self.save_note_btn.configure(state="disabled")
        self.cancel_note_btn = ctk.CTkButton(
            right, text="Cancel", command=self.cancel_browse_edit
        )
        self.cancel_note_btn.grid(row=5, column=0, sticky="e", padx=6, pady=(0, 2))
        self.cancel_note_btn.configure(state="disabled")

        # Export / Import
        ctk.CTkButton(right, text="Export", command=self.browse_export_note).grid(
            row=6, column=0, sticky="ew", padx=(6, 2), pady=(0, 8)
        )
        ctk.CTkButton(right, text="Import", command=self.browse_import_note).grid(
            row=6, column=1, sticky="ew", padx=(2, 6), pady=(0, 8)
        )

        def on_browse_right_click(event):
            selection = self.browse_listbox.nearest(event.y)
            if selection >= 0:
                self.browse_listbox.selection_clear(0, tk.END)
                self.browse_listbox.selection_set(selection)
                self.browse_listbox.activate(selection)
                menu = tk.Menu(self.browse_listbox, tearoff=0)
                menu.add_command(
                    label="Open in VS Code", command=self.browse_open_in_vscode
                )
                menu.add_command(
                    label="Open in Obsidian", command=self.browse_open_in_obsidian
                )
                menu.add_command(label="Preview", command=self.browse_preview_note)
                menu.add_separator()
                menu.add_command(label="Delete", command=self.browse_delete_note)
                menu.tk_popup(event.x_root, event.y_root)

        self.browse_listbox.bind("<Button-3>", on_browse_right_click)

        # now load & apply filters
        self._browse_load_notes()
        self._browse_filter_notes()

    def _browse_load_notes(self):
        # collect all notes and all wiki-link tags ([[Tag]])
        self.browse_notes = []
        self.all_tags = set()

        for folder, _, files in os.walk(self.config.VAULT_PATH):
            for fname in files:
                if not fname.lower().endswith(".md"):
                    continue

                # vault-relative path
                rel = os.path.relpath(
                    os.path.join(folder, fname), self.config.VAULT_PATH
                ).replace("\\", "/")
                self.browse_notes.append(rel)

                # read entire file for [[Tag]] patterns
                full = os.path.join(self.config.VAULT_PATH, rel)
                with open(full, encoding="utf-8") as f:
                    text = f.read()
                # extract each wiki-link as a tag
                for t in re.findall(r"\[\[([^\]]+)\]\]", text):
                    t = t.strip()
                    if t:
                        self.all_tags.add(t)

        self.browse_notes.sort()

    def _browse_filter_notes(self):
        # safely fetch filter values
        query = (
            self.browse_search_var.get().lower()
            if hasattr(self, "browse_search_var")
            else ""
        )
        tag = self.tag_filter_var.get() if hasattr(self, "tag_filter_var") else ""
        folder_filter = (
            self.folder_filter_var.get().replace("\\", "/")
            if hasattr(self, "folder_filter_var")
            else ""
        )

        # rebuild listbox
        self.browse_listbox.delete(0, tk.END)
        for note in self.browse_notes:
            note_folder = os.path.dirname(note).replace("\\", "/")
            full = os.path.join(self.config.VAULT_PATH, note)

            # tag filter: look for [[Tag]] in file
            if tag:
                with open(full, encoding="utf-8") as f:
                    body = f.read()
                if f"[[{tag}]]" not in body:
                    continue

            # folder filter
            if folder_filter and not note_folder.startswith(folder_filter):
                continue

            # text search
            if query and query not in note.lower():
                continue

            self.browse_listbox.insert(tk.END, note)

    def _browse_get_selection(self):
        idxs = self.browse_listbox.curselection()
        return [self.browse_listbox.get(i) for i in idxs] if idxs else []

    def browse_new_note(self):
        # Gather folders for dropdown
        folders = get_all_folders(self.config.VAULT_PATH)
        dialog = ctk.CTkToplevel(self)
        dialog.title("Create New Note")
        dialog.geometry("400x200")

        ctk.CTkLabel(dialog, text="File Name (no extension):").pack(pady=(14, 2))
        file_entry = ctk.CTkTextbox(dialog, height=28, width=340)
        file_entry.pack(pady=2)

        ctk.CTkLabel(dialog, text="Choose Folder:").pack(pady=(10, 2))
        folder_var = tk.StringVar(dialog)
        folder_var.set(self.folder_filter_var.get() or folders[0])
        folder_menu = ctk.CTkOptionMenu(
            dialog, variable=folder_var, values=folders, width=340
        )
        folder_menu.pack(pady=2)

        def do_create():
            filename = file_entry.get("1.0", "end").strip()
            filename = make_title_case_filename(filename)
            if not filename:
                messagebox.showerror("Error", "Please enter a valid file name.")
                self.status_var.set("Create failed: invalid file name.")
                return
            folder = folder_var.get()
            folder_path = (
                os.path.join(self.config.VAULT_PATH, folder)
                if folder
                else self.config.VAULT_PATH
            )
            os.makedirs(folder_path, exist_ok=True)
            filepath = os.path.join(folder_path, filename + ".md")
            if os.path.exists(filepath):
                messagebox.showerror("Error", "A note with that name already exists.")
                self.status_var.set("Create failed: file exists.")
                return
            try:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write("# " + filename.replace("_", " ") + "\n\n")
                self._browse_load_notes()
                self._browse_filter_notes()
                self.status_var.set(
                    f"New note created: {os.path.join(folder, filename + '.md')}"
                )
                dialog.destroy()
            except Exception as e:
                log_exception("Failed to create new note", e)
                messagebox.showerror("Error", f"Could not create file: \n{e}")
                self.status_var.set("Create failed.")

        btns = ctk.CTkFrame(dialog)
        btns.pack(pady=16)
        ctk.CTkButton(btns, text="Create", command=do_create, width=80).grid(
            row=0, column=0, padx=4
        )
        ctk.CTkButton(btns, text="Cancel", command=dialog.destroy, width=80).grid(
            row=0, column=1, padx=4
        )

        dialog.transient(self)
        dialog.grab_set()
        self.wait_window(dialog)

    def enable_browse_edit(self):
        self.browse_preview_box.configure(state="normal")
        self.save_note_btn.configure(state="normal")
        self.cancel_note_btn.configure(state="normal")
        self.edit_note_btn.configure(state="disabled")
        self.status_var.set(
            "Editing enabled. Make changes and click 'Save Changes' to save."
        )

    def browse_export_note(self):
        sel = self._browse_get_selection()
        if not sel:
            self.status_var.set("No note selected.")
            return
        src = os.path.join(self.config.VAULT_PATH, sel)
        default_name = os.path.basename(sel)
        dest = fd.asksaveasfilename(
            title="Export Note", defaultextension=".md", initialfile=default_name
        )
        if dest:
            try:
                with open(src, "r", encoding="utf-8") as fsrc, open(
                    dest, "w", encoding="utf-8"
                ) as fdest:
                    fdest.write(fsrc.read())
                self.status_var.set(f"Exported: {dest}")
            except Exception as e:
                log_exception(f"Export failed for {sel}", e)
                self.status_var.set("Export failed!")

    def browse_import_note(self):
        files = fd.askopenfilenames(
            title="Import Note(s)",
            filetypes=[("Markdown Files", "*.md"), ("All Files", "*.*")],
        )
        folder = self.folder_filter_var.get() or ""
        dest_folder = os.path.join(self.config.VAULT_PATH, folder)
        os.makedirs(dest_folder, exist_ok=True)
        imported = 0
        for src in files:
            name = os.path.basename(src)
            dest = os.path.join(dest_folder, name)
            try:
                with open(src, "r", encoding="utf-8") as fsrc, open(
                    dest, "w", encoding="utf-8"
                ) as fdest:
                    fdest.write(fsrc.read())
                imported += 1
            except Exception as e:
                log_exception(f"Import failed for {src}", e)
        self._browse_load_notes()
        self._browse_filter_notes()
        self.status_var.set(f"Imported {imported} note(s).")

    def browse_delete_note(self):
        sel = self._browse_get_selection()
        if not sel:
            self.status_var.set("No note selected.")
            return
        confirm = messagebox.askyesno(
            "Delete Note", f"Are you sure you want to permanently delete '{sel}'?"
        )
        if not confirm:
            return
        path = os.path.join(self.config.VAULT_PATH, sel)
        try:
            os.remove(path)
            self.status_var.set(f"Deleted: {sel}")
            self._browse_load_notes()
            self._browse_filter_notes()
            self.browse_preview_box.configure(state="normal")
            self.browse_preview_box.delete("1.0", "end")
            self.browse_preview_box.configure(state="disabled")
        except Exception as e:
            log_exception(f"Failed to delete note: {sel}", e)
            messagebox.showerror("Delete Failed", f"Could not delete: \n{e}")
            self.status_var.set("Delete failed.")

    def cancel_browse_edit(self):
        # Restore the original content and disable editing
        self.browse_preview_box.configure(state="normal")
        self.browse_preview_box.delete("1.0", END)
        self.browse_preview_box.insert("1.0", self.browse_original_content)
        self.browse_preview_box.configure(state="disabled")
        self.save_note_btn.configure(state="disabled")
        self.cancel_note_btn.configure(state="disabled")
        self.edit_note_btn.configure(state="normal")
        self.status_var.set("Edit canceled.")

    def browse_save_note(self):
        sel = self._browse_get_selection()
        if not sel:
            self.status_var.set("No note selected.")
            return
        path = os.path.join(self.config.VAULT_PATH, sel)
        new_content = self.browse_preview_box.get("1.0", END)
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(new_content)
            self.browse_preview_box.configure(state="disabled")
            self.save_note_btn.configure(state="disabled")
            self.status_var.set(f"Saved changes to: {sel}")
        except Exception as e:
            log_exception(f"Failed to save edited note: {sel}", e)
            self.status_var.set("Error saving note!")
        self.save_note_btn.configure(state="disabled")
        self.cancel_note_btn.configure(state="disabled")
        self.edit_note_btn.configure(state="normal")

    def browse_preview_note(self):
        sel_list = self._browse_get_selection()
        sel = sel_list[0] if sel_list else ""

        # Load raw text
        self.browse_preview_box.configure(state="normal")
        self.browse_preview_box.delete("1.0", END)
        if not sel:
            # nothing selected → clear everything
            if self.browse_html_preview:
                self.browse_html_preview.destroy()
                self.browse_html_preview = None
            self.browse_preview_box.insert("1.0", "")
            self.browse_preview_box.configure(state="disabled")
            self.save_note_btn.configure(state="disabled")
            self.edit_note_btn.configure(state="disabled")
            self.browse_preview_mode = "text"
            self.status_var.set("No note selected.")
            # re-grid raw box so layout stays consistent
            self.browse_preview_box.grid(
                row=1, column=0, columnspan=2, sticky="nsew", padx=6, pady=(0, 4)
            )
            return

        # Read file
        path = os.path.join(self.config.VAULT_PATH, sel)
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            content = f"[ERROR: {e}]"
        self.browse_original_content = content

        # Common button state
        self.save_note_btn.configure(state="disabled")
        self.cancel_note_btn.configure(state="disabled")
        self.edit_note_btn.configure(state="normal")

        # Decide which mode to show
        if self.browse_preview_mode == "html":
            # HTML-mode: hide raw, show rendered
            self.browse_preview_box.grid_remove()
            if self.browse_html_preview:
                self.browse_html_preview.destroy()
            html = markdown2.markdown(content)
            self.browse_html_preview = HTMLLabel(
                self.browse_preview_box.master,
                html=html,
                background="#23272e",
                foreground="#ECECEC",
            )
            # **always span 2 columns** so it stays the same width
            self.browse_html_preview.grid(
                row=1, column=0, columnspan=2, sticky="nsew", padx=6, pady=(0, 4)
            )
            self.status_var.set(f"Previewed (formatted): {sel}")
        else:
            # Text-mode: destroy HTML widget, show raw
            if self.browse_html_preview:
                self.browse_html_preview.destroy()
                self.browse_html_preview = None
            # make sure textbox is back in the grid
            self.browse_preview_box.grid(
                row=1, column=0, columnspan=2, sticky="nsew", padx=6, pady=(0, 4)
            )
            self.browse_preview_box.insert("1.0", content)
            self.browse_preview_box.configure(state="normal")
            self.status_var.set(f"Previewed (markdown): {sel}")

    def browse_open_in_vscode(self):
        sel = self._browse_get_selection()
        if not sel:
            self.status_var.set("No note selected.")
            return
        full = os.path.join(self.config.VAULT_PATH, sel)
        try:
            if not os.path.exists(full):
                raise FileNotFoundError
            if platform.system() == "Windows":
                os.startfile(full)
            else:
                import subprocess

                subprocess.Popen(["code", full])
            self.status_var.set(f"Opened in VS Code: {sel}")
        except Exception as e:
            log_exception(f"Failed to open in VS Code: {sel}", e)
            messagebox.showerror("Open Failed", f"Could not open in VS Code: \n{e}")
            self.status_var.set("Open in VS Code failed.")

    def browse_open_in_obsidian(self):
        sel_list = self._browse_get_selection()
        sel = sel_list[0] if sel_list else ""
        if not sel:
            self.status_var.set("No note selected.")
            return

        vault = os.path.basename(self.config.VAULT_PATH)
        # quote() expects a string, not a list
        path = urllib.parse.quote(sel, safe="")

        try:
            webbrowser.open(f"obsidian://open?vault={vault}&file={path}")
            self.status_var.set(f"Opened in Obsidian: {sel}")
        except Exception as e:
            log_exception(f"Failed to open in Obsidian: {sel}", e)
            messagebox.showerror("Open Failed", f"Could not open in Obsidian: \n{e}")
            self.status_var.set("Open in Obsidian failed.")

    def _setup_summarize_tab(self):
        tab = self.tabview.add("Summarize")
        tab.rowconfigure(0, weight=1)
        tab.columnconfigure(0, weight=1)

        main = ctk.CTkFrame(tab)
        main.grid(row=0, column=0, sticky="nsew", padx=12, pady=12)
        main.rowconfigure(0, weight=0)
        main.rowconfigure(1, weight=0)
        main.rowconfigure(2, weight=1)  # <- Make row for output expand
        main.columnconfigure(0, weight=1)  # <- Make output column expand

        ctk.CTkLabel(
            main, text="Summarize a folder of notes:", font=("Segoe UI", 15)
        ).grid(row=0, column=0, sticky="w", padx=6, pady=(14, 2))
        btn_summarize = ctk.CTkButton(
            main, text="Summarize Folder", command=self.summarize_folder, height=36
        )
        btn_summarize.grid(row=1, column=0, sticky="ew", padx=6, pady=(0, 8))
        ToolTip(
            btn_summarize,
            "Summarize all notes in the selected folder (great for campaign recaps!)",
        )
        self.summarize_output = ctk.CTkTextbox(
            main, font=("Consolas", 13), wrap="word", state="disabled"
        )
        self.summarize_output.grid(row=2, column=0, sticky="nsew", padx=6, pady=(2, 10))

    def summarize_folder(self):
        folders = get_all_folders(self.config.VAULT_PATH)
        dialog = ctk.CTkToplevel(self)
        dialog.title("Summarize Folder")
        dialog.geometry("400x140")

        ctk.CTkLabel(dialog, text="Choose Folder to Summarize:").pack(pady=(14, 2))
        folder_var = tk.StringVar(dialog)
        folder_var.set(folders[0])
        folder_menu = ctk.CTkOptionMenu(
            dialog, variable=folder_var, values=folders, width=340
        )
        folder_menu.pack(pady=2)

        def do_summarize():
            folder = folder_var.get()
            folder_path = (
                os.path.join(self.config.VAULT_PATH, folder)
                if folder
                else self.config.VAULT_PATH
            )
            texts = []
            try:
                for fname in os.listdir(folder_path):
                    if fname.endswith(".md"):
                        try:
                            with open(
                                os.path.join(folder_path, fname), "r", encoding="utf-8"
                            ) as f:
                                texts.append(f.read())
                        except Exception:
                            self.status_var.set(f"Failed to read: {fname}")
                if not texts:
                    messagebox.showwarning("No Notes", "No .md files in that folder!")
                    self.status_var.set("No notes found to summarize.")
                    dialog.destroy()
                    return
                joined = "\n\n".join(texts)
                summary_prompt = f"Summarize the following campaign notes in a concise and organized way for later reference: \n\n{joined}"
                model = "gpt-3.5-turbo"
                prompt_tokens = count_tokens(summary_prompt, model)
                if not self._check_token_permission(prompt_tokens):
                    self.status_var.set("Request cancelled (too large).")
                    dialog.destroy()
                    return
                answer = self.ai.query(summary_prompt)
                response_tokens = count_tokens(str(answer), model)
                self.session_tokens += prompt_tokens + response_tokens
                self.last_answer = answer
                self.summarize_output.configure(state="normal")
                self.summarize_output.delete("1.0", END)
                self.summarize_output.insert("1.0", self.last_answer)
                self.summarize_output.configure(state="disabled")
                self.status_var.set(
                    f"Summarized {len(texts)} notes in {folder_path}. Session tokens: {self.session_tokens}"
                )
                if hasattr(self, "token_label"):
                    self.token_label.configure(
                        text=f"Session tokens used: {self.session_tokens}"
                    )
                dialog.destroy()

            except Exception as e:
                log_exception("Failed to summarize folder", e)
                messagebox.showerror("Error", f"Summarizing failed: \n{e}")
                self.status_var.set("Summarizing failed.")
                dialog.destroy()

        ctk.CTkButton(dialog, text="Summarize", command=do_summarize, width=80).pack(
            pady=16
        )
        dialog.transient(self)
        dialog.grab_set()
        self.wait_window(dialog)

    def _setup_help_tab(self):
        tab = self.tabview.add("Help / About")
        tab.rowconfigure(0, weight=1)
        tab.columnconfigure(0, weight=1)

        help_frame = ctk.CTkFrame(tab)
        help_frame.grid(row=0, column=0, sticky="nsew", padx=30, pady=30)
        help_frame.rowconfigure(0, weight=1)
        help_frame.columnconfigure(0, weight=1)

        help_text = (
            "Welcome to the Obsidian Lore Assistant!\n\n"
            "• **Ask AI Tab:**\n"
            "  - Type your D&D/worldbuilding question and click 'Ask'.\n"
            "  - Save, split, or preview notes as Markdown.\n"
            "  - Conversation history keeps a running log of your Q&A.\n\n"
            "• **Browse Vault Tab: **\n"
            "  - Search and browse all your .md notes.\n"
            "  - Open notes in VS Code or Obsidian.\n"
            "  - Preview note content directly in-app.\n\n"
            "• **Summarize Tab: **\n"
            "  - Summarize all notes in any folder for quick campaign recaps.\n\n"
            "Tips: \n"
            "- Hover over any button for a tooltip explaining its function.\n"
            "- All windows and sections resize automatically.\n"
            "- Need more? Ask for more help in this tab!"
        )
        box = ctk.CTkTextbox(
            help_frame,
            font=("Segoe UI", 13),
            wrap="word",
            state="normal",
            width=800,
            height=400,
        )
        box.insert("1.0", help_text)
        box.configure(state="disabled")
        box.grid(row=0, column=0, sticky="nsew")

    def ask_question(self):
        question = self.input_box.get("1.0", END).strip()
        if not question:
            self.status_var.set("Please enter a prompt.")
            self.save_note_btn.configure(state="disabled")
            self.split_note_btn.configure(state="disabled")
            return

        model = "gpt-3.5-turbo"
        prompt_tokens = count_tokens(question, model)
        if not self._check_token_permission(prompt_tokens):
            self.status_var.set("Request cancelled (too large).")
            return
        answer = self.ai.query(question)
        response_tokens = count_tokens(str(answer), model)
        self.session_tokens += prompt_tokens + response_tokens
        self.last_answer = answer
        self.save_note_btn.configure(state="normal")
        self.split_note_btn.configure(state="normal")
        self.output_box.configure(state="normal")
        self.output_box.delete("1.0", END)
        self.output_box.insert("1.0", self.last_answer)
        self.output_box.configure(state="disabled")
        entry = f"---\nPrompt: {question}\n\nAI Response:\n{self.last_answer}\n"
        self.history.append(entry)
        self.history_text.configure(state="normal")
        self.history_text.insert(END, entry)
        self.history_text.see(END)
        self.history_text.configure(state="disabled")
        self.status_var.set(f"Answer generated. Session tokens: {self.session_tokens}")
        if hasattr(self, "token_label"):
            self.token_label.configure(
                text=f"Session tokens used: {self.session_tokens}"
            )

    def clear_history(self):
        self.history = []
        self.history_text.configure(state="normal")
        self.history_text.delete("1.0", END)
        self.history_text.configure(state="disabled")
        self.status_var.set("History cleared.")
        self.save_note_btn.configure(state="disabled")
        self.split_note_btn.configure(state="disabled")

    def preview_in_browser(self, markdown_text):
        html = markdown2.markdown(markdown_text)
        html = f"""
        <html>
        <head>
        <style>
        body {{
            font-family: Segoe UI, Arial, sans-serif;
            max-width: 700px;
            margin: 30px auto;
            background: #18191A;
            color: #ECECEC;
        }}
        h1, h2, h3 {{ color: #63aaff; }}
        code, pre {{
            background: #282C34;
            color: #FFD580;
            padding: 2px 6px;
            border-radius: 4px;
        }}
        a {{ color: #ffbe76; }}
        </style>
        </head>
        <body>{html}</body>
        </html>
        """
        with tempfile.NamedTemporaryFile(
            "w", delete=False, suffix=".html", encoding="utf-8"
        ) as f:
            f.write(html)
            tempname = f.name
        webbrowser.open(f"file://{tempname}")

    # --- NOTE MANAGEMENT ---

    def save_note(self):
        if not self.last_answer:
            messagebox.showwarning("No Answer", "Ask a question first!")
            self.status_var.set("No answer to save.")
            return
        folders = get_all_folders(self.config.VAULT_PATH)
        dialog = ctk.CTkToplevel(self)
        dialog.title("Save Note")
        dialog.geometry("400x180")

        ctk.CTkLabel(dialog, text="File Name (no extension):").pack(pady=(10, 2))
        file_entry = ctk.CTkTextbox(dialog, height=28, width=340)
        suggested_name = make_title_case_filename(self.input_box.get("1.0", END))
        file_entry.insert("1.0", suggested_name)
        file_entry.pack(pady=2)

        ctk.CTkLabel(dialog, text="Choose Folder:").pack(pady=(10, 2))
        folder_var = tk.StringVar(dialog)
        folder_var.set(folders[0])
        folder_menu = ctk.CTkOptionMenu(
            dialog, variable=folder_var, values=folders, width=340
        )
        folder_menu.pack(pady=2)

        def do_save():
            filename = file_entry.get("1.0", END).strip()
            filename = make_title_case_filename(filename)
            if not filename:
                messagebox.showerror("Error", "Please enter a valid file name.")
                self.status_var.set("Save failed: invalid file name.")
                return
            folder = folder_var.get()
            folder_path = (
                os.path.join(self.config.VAULT_PATH, folder)
                if folder
                else self.config.VAULT_PATH
            )
            os.makedirs(folder_path, exist_ok=True)
            filepath = os.path.join(folder_path, filename + ".md")
            note_names = get_note_names(self.config.VAULT_PATH)
            linked_answer = auto_link_notes(self.last_answer, note_names)
            try:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(f"# {filename}\n")
                    f.write(
                        f"*Generated on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}*\n\n"
                    )
                    f.write(f"**Prompt:** {self.input_box.get('1.0', END).strip()}\n\n")
                    f.write(linked_answer)
                messagebox.showinfo("Saved!", f"Saved to {filepath}")
                self.status_var.set(f"Saved note: {filepath}")
                dialog.destroy()
            except Exception as e:
                log_exception("Failed to save note", e)
                messagebox.showerror("Error Saving File", f"Failed to save file: \n{e}")
                self.status_var.set("Save failed.")

        ctk.CTkButton(dialog, text="Save", command=do_save, width=80).pack(pady=14)
        dialog.transient(self)
        dialog.grab_set()
        self.wait_window(dialog)

    def split_and_save_multiple(self):
        if not self.last_answer:
            messagebox.showwarning("No Answer", "Ask a question first!")
            self.status_var.set("No answer to split & save.")
            return

        folders = get_all_folders(self.config.VAULT_PATH)
        dialog = ctk.CTkToplevel(self)
        dialog.title("Save Multiple Notes")
        dialog.geometry("400x130")

        ctk.CTkLabel(dialog, text="Choose Folder to Save Notes:").pack(pady=(14, 2))
        folder_var = tk.StringVar(dialog)
        folder_var.set(folders[0])
        folder_menu = ctk.CTkOptionMenu(
            dialog, variable=folder_var, values=folders, width=340
        )
        folder_menu.pack(pady=2)

        def do_save_all():
            folder = folder_var.get()
            folder_path = (
                os.path.join(self.config.VAULT_PATH, folder)
                if folder
                else self.config.VAULT_PATH
            )
            os.makedirs(folder_path, exist_ok=True)
            parts = re.split(r"(?=^# )", self.last_answer, flags=re.MULTILINE)
            note_names = get_note_names(self.config.VAULT_PATH)
            count = 0
            errors = []

            for part in parts:
                lines = part.strip().split("\n", 1)
                if not part.strip() or not lines[0].startswith("#"):
                    continue

                heading = lines[0][2:].strip()
                body = lines[1].strip() if len(lines) > 1 else ""
                filename = make_title_case_filename(heading)
                linked_body = auto_link_notes(body, note_names)
                filepath = os.path.join(folder_path, filename + ".md")

                try:
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(f"# {heading}\n")
                        f.write(
                            f"*Generated on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}*\n\n"
                        )
                        f.write(
                            f"**Prompt:** {self.input_box.get('1.0', END).strip()}\n\n"
                        )
                        f.write(linked_body)
                    count += 1
                except Exception as ex:
                    log_exception(f"Failed to save split note: {filename}", ex)
                    errors.append(filename)

            if errors:
                messagebox.showwarning(
                    "Partial Save", f"Some notes failed to save: {', '.join(errors)}"
                )
            else:
                messagebox.showinfo("Done", f"Saved {count} notes to {folder_path}")
            self.status_var.set(f"Saved {count} notes to {folder_path}")
            dialog.destroy()

        ctk.CTkButton(dialog, text="Save All", command=do_save_all, width=90).pack(
            pady=16
        )
        dialog.transient(self)
        dialog.grab_set()
        self.wait_window(dialog)

    def _setup_random_generator_tab(self):
        tab = self.tabview.add("Random Generator")
        tab.rowconfigure(0, weight=1)
        tab.columnconfigure(0, weight=1)
        main = ctk.CTkFrame(tab)
        main.grid(row=0, column=0, sticky="nsew", padx=12, pady=12)
        ctk.CTkLabel(
            main, text="Random Generator Features Coming Soon", font=("Segoe UI", 15)
        ).pack(pady=30)

    def _setup_timeline_tab(self):
        tab = self.tabview.add("Timeline")
        tab.rowconfigure(0, weight=1)
        tab.columnconfigure(0, weight=1)
        main = ctk.CTkFrame(tab)
        main.grid(row=0, column=0, sticky="nsew", padx=12, pady=12)
        ctk.CTkLabel(
            main, text="Timeline Features Coming Soon", font=("Segoe UI", 15)
        ).pack(pady=30)

    def _setup_campaign_settings_tab(self):
        tab = self.tabview.add("Campaign Settings")
        tab.rowconfigure(0, weight=1)
        tab.columnconfigure(0, weight=1)
        main = ctk.CTkFrame(tab)
        main.grid(row=0, column=0, sticky="nsew", padx=12, pady=12)
        ctk.CTkLabel(
            main, text="Campaign Settings Features Coming Soon", font=("Segoe UI", 15)
        ).pack(pady=30)

    def _check_token_permission(self, token_count):
        if token_count >= self.token_limit:
            result = messagebox.askyesno(
                "Large Request",
                f"This request will use about {token_count} tokens.\nProceed?",
            )
            return result
        return True

    def _update_token_limit(self):
        try:
            new_limit = int(self.token_limit_entry.get("1.0", "end").strip())
            self.token_limit = new_limit
            self.status_var.set(f"Token limit updated: {self.token_limit}")
        except ValueError:
            self.status_var.set("Invalid limit.")

    def _setup_token_tab(self):
        tab = self.tabview.add("Tokens")
        tab.rowconfigure(0, weight=1)
        tab.columnconfigure(0, weight=1)
        main = ctk.CTkFrame(tab)
        main.grid(row=0, column=0, sticky="nsew", padx=24, pady=24)
        ctk.CTkLabel(main, text="Token Usage Info", font=("Segoe UI", 15, "bold")).pack(
            pady=(0, 12)
        )
        self.token_label = ctk.CTkLabel(
            main,
            text=f"Session tokens used: {self.session_tokens}",
            font=("Consolas", 13),
        )
        self.token_label.pack(pady=4)
        ctk.CTkLabel(main, text="Token limit before warning:").pack()
        self.token_limit_entry = ctk.CTkTextbox(main, height=24, width=100)
        self.token_limit_entry.insert("1.0", str(self.token_limit))
        self.token_limit_entry.pack()
        ctk.CTkButton(main, text="Set Limit", command=self._update_token_limit).pack(
            pady=4
        )

    def browse_ai_summarize(self):
        sel = self._browse_get_selection()
        if not sel:
            self.status_var.set("No note selected.")
            return
        path = os.path.join(self.config.VAULT_PATH, sel)
        with open(path, "r", encoding="utf-8") as f:
            note_text = f.read()
        summary, prompt_tokens, response_tokens = self.ai.summarize(note_text)
        if not self._check_token_permission(prompt_tokens):
            self.status_var.set("Request cancelled (too large).")
            return
        self.session_tokens += prompt_tokens + response_tokens
        # Show summary in a popup
        popup = ctk.CTkToplevel(self)
        popup.title("AI Summary")
        popup.geometry("600x350")
        out = ctk.CTkTextbox(popup, font=("Consolas", 13), wrap="word")
        out.insert("1.0", summary)
        out.configure(state="disabled")
        out.pack(expand=True, fill="both", padx=10, pady=10)
        ctk.CTkButton(popup, text="Close", command=popup.destroy).pack(pady=6)
        self.status_var.set(f"Note summarized. Session tokens: {self.session_tokens}")
        if hasattr(self, "token_label"):
            self.token_label.configure(
                text=f"Session tokens used: {self.session_tokens}"
            )

    def next_tab(self, event=None):
        tabs = self.tabview._tab_dict
        keys = list(tabs.keys())
        current = self.tabview.get()
        if current in keys:
            idx = keys.index(current)
            next_idx = (idx + 1) % len(keys)
            self.tabview.set(keys[next_idx])

    def prev_tab(self, event=None):
        tabs = self.tabview._tab_dict
        keys = list(tabs.keys())
        current = self.tabview.get()
        if current in keys:
            idx = keys.index(current)
            prev_idx = (idx - 1) % len(keys)
            self.tabview.set(keys[prev_idx])

    def try_undo(self):
        widget = self.focus_get()
        try:
            widget.edit_undo()
        except Exception:
            pass

    def try_redo(self):
        widget = self.focus_get()
        try:
            widget.edit_redo()
        except Exception:
            pass

    def find_text(self):
        widget = self.focus_get()
        if not hasattr(widget, "search"):
            self.status_var.set("Find: Focus a text box.")
            return

        def do_find():
            target = entry.get()
            if not target:
                return
            start = widget.search(target, "1.0", tk.END)
            if start:
                end = f"{start}+{len(target)}c"
                widget.tag_remove("find_highlight", "1.0", tk.END)
                widget.tag_add("find_highlight", start, end)
                widget.tag_config(
                    "find_highlight", background="#ffe066", foreground="#23272e"
                )
                widget.see(start)
                self.status_var.set(f'Found "{target}".')
            else:
                widget.tag_remove("find_highlight", "1.0", tk.END)
                self.status_var.set(f'"{target}" not found.')

        dialog = ctk.CTkToplevel(self)
        dialog.title("Find")
        dialog.geometry("300x90")
        ctk.CTkLabel(dialog, text="Find:").pack(pady=(12, 3))
        entry = ctk.CTkEntry(dialog)
        entry.pack(pady=(0, 6), padx=16, fill="x")
        entry.focus_set()
        ctk.CTkButton(dialog, text="Find", command=lambda: do_find()).pack(pady=(0, 10))
        dialog.transient(self)
        dialog.grab_set()
        self.wait_window(dialog)

    def replace_text(self):
        widget = self.focus_get()
        if not hasattr(widget, "search"):
            self.status_var.set("Replace: Focus a text box.")
            return

        def do_replace():
            target = entry_find.get()
            repl = entry_replace.get()
            if not target:
                return
            idx = widget.search(target, "1.0", tk.END)
            count = 0
            while idx:
                end = f"{idx}+{len(target)}c"
                widget.delete(idx, end)
                widget.insert(idx, repl)
                count += 1
                idx = widget.search(target, end, tk.END)
            self.status_var.set(f"Replaced {count} occurrence(s).")

        dialog = ctk.CTkToplevel(self)
        dialog.title("Replace")
        dialog.geometry("320x140")
        ctk.CTkLabel(dialog, text="Find:").pack(pady=(10, 1))
        entry_find = ctk.CTkEntry(dialog)
        entry_find.pack(pady=(0, 8), padx=16, fill="x")
        entry_find.focus_set()
        ctk.CTkLabel(dialog, text="Replace with:").pack(pady=(0, 1))
        entry_replace = ctk.CTkEntry(dialog)
        entry_replace.pack(pady=(0, 8), padx=16, fill="x")
        ctk.CTkButton(dialog, text="Replace All", command=lambda: do_replace()).pack(
            pady=(2, 12)
        )
        dialog.transient(self)
        dialog.grab_set()
        self.wait_window(dialog)

    def highlight_markdown(self, textbox):
        # Remove old tags
        for tag in textbox.tag_names():
            textbox.tag_remove(tag, "1.0", "end")
        text = textbox.get("1.0", "end")
        # Headers (#)
        for match in re.finditer(r"^(#+ .+)$", text, flags=re.MULTILINE):
            start_idx = f"1.0+{match.start(1)}c"
            end_idx = f"1.0+{match.end(1)}c"
            textbox.tag_add("header", start_idx, end_idx)
        textbox.tag_config(
            "header", foreground="#63aaff", font=("Segoe UI", 14, "bold")
        )
        # Bold (**)
        for match in re.finditer(r"\*\*(.+?)\*\*", text):
            start_idx = f"1.0+{match.start(1)}c"
            end_idx = f"1.0+{match.end(1)}c"
            textbox.tag_add("bold", start_idx, end_idx)
        textbox.tag_config("bold", font=("Segoe UI", 13, "bold"))
        # Inline code (`code`)
        for match in re.finditer(r"`([^`]+)`", text):
            start_idx = f"1.0+{match.start(1)}c"
            end_idx = f"1.0+{match.end(1)}c"
            textbox.tag_add("code", start_idx, end_idx)
        textbox.tag_config(
            "code",
            background="#282C34",
            foreground="#FFD580",
            font=("Consolas", 12, "bold"),
        )

    def toggle_browse_preview(self):
        sel_list = self._browse_get_selection()
        sel = sel_list[0] if sel_list else ""
        if not sel:
            self.status_var.set("No note selected.")
            return

        path = os.path.join(self.config.VAULT_PATH, sel)
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            content = f"[ERROR: {e}]"

        if self.browse_html_preview:
            self.browse_html_preview.destroy()
            self.browse_html_preview = None
        if self.browse_preview_box:
            self.browse_preview_box.destroy()
            self.browse_preview_box = None

        if self.browse_preview_mode == "text":
            css = """
            <style>
            h1, h2, h3 { color: #f39c12; }
            .tag { background: #27ae60; color: white;
                    padding: 2px 6px; border-radius: 4px; }
            </style>
            """
            html = css + markdown2.markdown(content)

            self.browse_html_preview = HTMLLabel(
                self.browse_preview_container,
                html=html,
                background="#23272e",
                foreground="#ECECEC",
            )
            self.browse_html_preview.grid(
                row=1, column=0, columnspan=2, sticky="nsew", padx=6, pady=(0, 4)
            )
            self.preview_toggle_btn.configure(text="Markdown View")
            self.browse_preview_mode = "html"

        else:
            self.browse_preview_box = ctk.CTkTextbox(
                self.browse_preview_container,
                font=("Consolas", 12),
                state="normal",
                wrap="word",
            )
            self.browse_preview_box.insert("1.0", content)
            self.browse_preview_box.configure(state="disabled")
            self.browse_preview_box.grid(
                row=1, column=0, columnspan=2, sticky="nsew", padx=6, pady=(0, 4)
            )
            self.preview_toggle_btn.configure(text="HTML View")
            self.browse_preview_mode = "text"

        # end
