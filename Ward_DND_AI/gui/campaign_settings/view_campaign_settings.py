import tkinter as tk

import customtkinter as ctk


class CampaignSettingsView:
    """
    UI for configuring the Obsidian vault path and OpenAI API key.
    """

    def __init__(self, parent, config):
        self.config = config
        # Main container frame
        self.frame = ctk.CTkFrame(parent)
        self.frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # Vault Path
        ctk.CTkLabel(self.frame, text="Vault Path:", font=("Segoe UI", 12)).grid(
            row=0, column=0, sticky="w", pady=(0, 5)
        )
        self.vault_entry = ctk.CTkEntry(self.frame)
        # Pre-fill with existing config value
        self.vault_entry.insert(0, self.config.VAULT_PATH)
        self.vault_entry.grid(row=0, column=1, sticky="ew", padx=(5, 0), pady=(0, 5))

        # OpenAI API Key
        ctk.CTkLabel(self.frame, text="OpenAI API Key:", font=("Segoe UI", 12)).grid(
            row=1, column=0, sticky="w", pady=(0, 5)
        )
        self.api_entry = ctk.CTkEntry(self.frame, show="*")
        self.api_entry.insert(0, self.config.OPENAI_API_KEY)
        self.api_entry.grid(row=1, column=1, sticky="ew", padx=(5, 0), pady=(0, 5))

        # Save Button
        self.save_btn = ctk.CTkButton(self.frame, text="Save Settings")
        self.save_btn.grid(row=2, column=0, columnspan=2, pady=(10, 0))

        # Status Label (for feedback after save)
        self.status_var = tk.StringVar()
        self.status_label = ctk.CTkLabel(
            self.frame, textvariable=self.status_var, font=("Segoe UI", 10)
        )
        self.status_label.grid(row=3, column=0, columnspan=2, sticky="w", pady=(5, 0))

        # Allow second column (entries) to expand
        self.frame.columnconfigure(1, weight=1)
