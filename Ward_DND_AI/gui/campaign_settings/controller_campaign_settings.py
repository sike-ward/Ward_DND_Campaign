import os
import tkinter as tk
from pathlib import Path
from tkinter import messagebox


class CampaignSettingsController:
    def __init__(self, view, ai, storage, config, status_var=None):
        self.view = view
        self.ai = ai
        self.storage = storage
        self.config = config
        self.status_var = status_var or tk.StringVar()

        # Populate fields
        self.view.vault_entry.insert(0, self.config.VAULT_PATH)
        self.view.api_entry.insert(0, self.config.OPENAI_API_KEY)

        self.view.save_btn.configure(command=self.on_save)
        self.view.reset_btn.configure(command=self.reset_defaults) if hasattr(
            self.view, "reset_btn"
        ) else None

        # Auto-detect vault if blank or invalid
        if not self.config.VAULT_PATH or not os.path.exists(self.config.VAULT_PATH):
            self.auto_detect_vault()

    def auto_detect_vault(self):
        vault_candidates = Path.home().rglob("*.obsidian")
        for vault in vault_candidates:
            vault_root = vault.parent
            self.view.vault_entry.delete(0, tk.END)
            self.view.vault_entry.insert(0, str(vault_root))
            self.status_var.set(f"📁 Auto-detected vault: {vault_root}")
            return

    def reset_defaults(self):
        self.config.reset()
        self.view.vault_entry.delete(0, tk.END)
        self.view.vault_entry.insert(0, self.config.VAULT_PATH)
        self.view.api_entry.delete(0, tk.END)
        self.view.api_entry.insert(0, self.config.OPENAI_API_KEY)
        self.status_var.set("🔄 Settings reset to default.")

    def on_save(self):
        vp = self.view.vault_entry.get().strip().rstrip("\\/")
        key = self.view.api_entry.get().strip()

        if not vp or not key:
            messagebox.showerror("Error", "Vault path and API key are required.")
            self.status_var.set("❌ Save failed: missing input.")
            return

        # Validate/create vault path
        if not os.path.exists(vp):
            if messagebox.askyesno("Vault Path Missing", f"Create folder?\n{vp}"):
                try:
                    os.makedirs(vp)
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to create folder: {e}")
                    self.status_var.set("❌ Vault creation failed.")
                    return

        # Optional: ping AI to validate key (placeholder only)
        # try:
        #     self.ai.validate_key(key)  # if supported
        # except Exception:
        #     messagebox.showerror("Invalid Key", "The OpenAI key appears invalid.")
        #     self.status_var.set("❌ Invalid API key.")
        #     return

        self.config.VAULT_PATH = vp
        self.config.OPENAI_API_KEY = key
        self.config.save()

        self.status_var.set("✅ Settings updated.")
