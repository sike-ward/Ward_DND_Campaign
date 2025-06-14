import tkinter as tk

import customtkinter as ctk


class AskView:
    """
    View for the Ask AI tab.
    Contains prompt input, action buttons, output and history display, and status bar.
    """

    def __init__(self, parent, config):
        self.config = config
        self.frame = ctk.CTkFrame(parent)

        # Configure grid weights
        for i in range(5):
            self.frame.columnconfigure(i, weight=1)
        self.frame.rowconfigure(1, weight=2)  # output
        self.frame.rowconfigure(2, weight=1)  # history

        # Prompt input
        self.prompt_box = ctk.CTkTextbox(self.frame, height=100, wrap="word", undo=True)
        self.prompt_box.grid(
            row=0, column=0, columnspan=3, sticky="nsew", padx=6, pady=(8, 4)
        )

        # Action buttons
        self.ask_btn = ctk.CTkButton(self.frame, text="Ask AI")
        self.save_btn = ctk.CTkButton(self.frame, text="Save Answer", state="disabled")
        self.split_btn = ctk.CTkButton(
            self.frame, text="Split & Save", state="disabled"
        )
        self.clear_btn = ctk.CTkButton(self.frame, text="Clear History")
        self.preview_btn = ctk.CTkButton(self.frame, text="Preview", command=None)

        self.ask_btn.grid(row=0, column=3, padx=4, pady=(8, 4), sticky="ew")
        self.save_btn.grid(row=0, column=4, padx=4, pady=(8, 4), sticky="ew")
        self.split_btn.grid(row=1, column=3, padx=4, pady=(0, 4), sticky="ew")
        self.clear_btn.grid(row=1, column=4, padx=4, pady=(0, 4), sticky="ew")
        self.preview_btn.grid(row=0, column=2, padx=(6, 0))

        # AI output display
        self.output_box = ctk.CTkTextbox(
            self.frame, wrap="word", state="disabled", undo=True
        )
        self.output_box.grid(
            row=1, column=0, columnspan=3, sticky="nsew", padx=6, pady=(0, 8)
        )

        # Conversation history
        self.history_text = ctk.CTkTextbox(
            self.frame, wrap="word", state="disabled", undo=True
        )
        self.history_text.grid(
            row=2, column=0, columnspan=5, sticky="nsew", padx=6, pady=(0, 8)
        )

        # Status bar
        self.status_var = tk.StringVar()
        self.status_label = ctk.CTkLabel(
            self.frame, textvariable=self.status_var, anchor="w"
        )
        self.status_label.grid(
            row=3, column=0, columnspan=5, sticky="ew", padx=6, pady=(0, 6)
        )

    def grid(self, **kwargs):
        """Expose frame.grid for external layout."""
        self.frame.grid(**kwargs)
