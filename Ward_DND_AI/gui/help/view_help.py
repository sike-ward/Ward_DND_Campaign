# Ward_DND_AI/gui/help/view_help.py

import customtkinter as ctk


class HelpView:
    def __init__(self, parent, config):
        self.config = config
        self.frame = ctk.CTkFrame(parent)
        self.frame.rowconfigure(0, weight=1)
        self.frame.columnconfigure(0, weight=1)

        help_frame = ctk.CTkFrame(self.frame)
        help_frame.grid(row=0, column=0, sticky="nsew", padx=30, pady=30)
        help_frame.rowconfigure(0, weight=1)
        help_frame.columnconfigure(0, weight=1)

        self.box = ctk.CTkTextbox(
            help_frame,
            font=("Segoe UI", 13),
            wrap="word",
            state="disabled",
            width=800,
            height=400,
        )
        self.box.grid(row=0, column=0, sticky="nsew")

    def set_text(self, text: str):
        self.box.configure(state="normal")
        self.box.delete("1.0", "end")
        self.box.insert("1.0", text)
        self.box.configure(state="disabled")

    def grid(self, **kwargs):
        self.frame.grid(**kwargs)
