import tkinter as tk
from tkinter import ttk

import customtkinter as ctk


class BrowseView:
    def __init__(self, parent, config):
        self.config = config
        self.frame = ctk.CTkFrame(parent)
        # -- Layout grid --
        self.frame.rowconfigure(1, weight=1)
        self.frame.columnconfigure(0, weight=1)
        self.frame.columnconfigure(1, weight=3)

        # --- Top bar: folder filter, New, Import ---
        top = ctk.CTkFrame(self.frame)
        top.grid(row=0, column=0, columnspan=2, sticky="ew", padx=6, pady=6)
        self.folder_filter_var = tk.StringVar(value="")
        self.folder_menu = ctk.CTkOptionMenu(
            top, variable=self.folder_filter_var, values=[]
        )
        self.folder_menu.pack(side="left", padx=(0, 12))
        self.new_btn = ctk.CTkButton(top, text="New", width=60)
        self.import_btn = ctk.CTkButton(top, text="Import", width=60)
        self.new_btn.pack(side="left", padx=4)
        self.import_btn.pack(side="left", padx=4)

        # --- Left pane: notes list ---
        left = ctk.CTkFrame(self.frame)
        left.grid(row=1, column=0, sticky="nsew", padx=(6, 4), pady=(0, 6))
        left.rowconfigure(0, weight=1)
        left.columnconfigure(0, weight=1)
        self.notes_listbox = tk.Listbox(left, exportselection=False)
        self.notes_listbox.grid(row=0, column=0, sticky="nsew")
        self.notes_scroll = ttk.Scrollbar(
            left, orient="vertical", command=self.notes_listbox.yview
        )
        self.notes_listbox.configure(yscrollcommand=self.notes_scroll.set)
        self.notes_scroll.grid(row=0, column=1, sticky="ns")

        # --- Right pane: preview & controls ---
        right = ctk.CTkFrame(self.frame)
        right.grid(row=1, column=1, sticky="nsew", padx=(4, 6), pady=(0, 6))
        right.rowconfigure(1, weight=1)
        right.columnconfigure(0, weight=1)

        # Buttons: Edit / Save / Cancel / Toggle
        ctrl = ctk.CTkFrame(right)
        ctrl.grid(row=0, column=0, sticky="ew", pady=(0, 4))
        self.edit_btn = ctk.CTkButton(ctrl, text="Edit", width=80)
        self.save_btn = ctk.CTkButton(ctrl, text="Save", width=80)
        self.cancel_btn = ctk.CTkButton(ctrl, text="Cancel", width=80)
        self.toggle_btn = ctk.CTkButton(ctrl, text="HTML View", width=80)
        for b in (self.edit_btn, self.save_btn, self.cancel_btn, self.toggle_btn):
            b.pack(side="left", padx=4)

        # Containers for preview widgets (created by controller)
        self.preview_container = right
        self.text_preview = None
        self.html_preview = None

        # --- Status bar ---
        self.status_var = tk.StringVar()
        self.status_label = ctk.CTkLabel(
            self.frame, textvariable=self.status_var, anchor="w"
        )
        self.status_label.grid(
            row=2, column=0, columnspan=2, sticky="ew", padx=6, pady=(0, 6)
        )

    def grid(self, **kwargs):
        self.frame.grid(**kwargs)
