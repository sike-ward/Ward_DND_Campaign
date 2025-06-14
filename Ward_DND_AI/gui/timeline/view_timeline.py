import tkinter as tk

import customtkinter as ctk


class TimelineView:
    def __init__(self, parent):
        # Container frame for the tab
        self.frame = ctk.CTkFrame(parent)
        self.frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Entry for new events
        ctk.CTkLabel(
            self.frame, text="New Timeline Event:", font=("Segoe UI", 12)
        ).pack(anchor="w")
        self.event_entry = ctk.CTkEntry(self.frame)
        self.event_entry.pack(fill="x", pady=(0, 10))

        # Action buttons
        self.add_btn = ctk.CTkButton(self.frame, text="Add Event")
        self.add_btn.pack(pady=(0, 6))

        self.edit_btn = ctk.CTkButton(self.frame, text="Edit Selected")
        self.edit_btn.pack(pady=(0, 6))

        self.delete_btn = ctk.CTkButton(self.frame, text="Delete Selected")
        self.delete_btn.pack(pady=(0, 6))

        self.clear_btn = ctk.CTkButton(self.frame, text="Clear Timeline")
        self.clear_btn.pack(pady=(0, 10))

        # Listbox for displaying events
        self.event_list = tk.Listbox(self.frame, height=15, font=("Consolas", 12))
        self.event_list.pack(fill="both", expand=True)
