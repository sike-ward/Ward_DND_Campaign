"""
Ward_DND_AI/gui/token/controller_token.py

Controller for the Token tab: wires up the TokenView to storage and config,
handles pre-filling fields and saving model changes.
"""
import tkinter as tk


class TokenController:
    def __init__(self, view, ai, storage, config, status_var=None):
        self.view = view
        self.ai = ai
        self.storage = storage
        self.config = config
        self.status_var = status_var or tk.StringVar()

        # Wire up buttons
        self.view.refresh_btn.configure(command=self.update_usage)
        self.view.save_btn.configure(command=self.save_model_settings)

        # Pre-fill fields from config
        self.view.model_entry.insert(0, getattr(self.config, "MODEL", ""))
        self.view.temp_slider.set(getattr(self.config, "TEMPERATURE", 1.0))
        self.view.token_entry.insert(0, str(getattr(self.config, "MAX_TOKENS", 1000)))

        # Initial usage display
        self.update_usage()

    def update_usage(self):
        # Retrieve usage stats
        used = getattr(self.ai, "session_tokens", 0)
        limit = getattr(
            self.config, "TOKEN_LIMIT", getattr(self.config, "MAX_TOKENS", 0)
        )
        cost_estimate = getattr(self.ai, "estimated_cost_usd", None)

        display_text = f"Sessions: {used} / {limit}"
        if cost_estimate is not None:
            display_text += f" • Est: ${cost_estimate:.2f}"

        self.view.usage_label.configure(text=display_text)

        # Warn if near limit
        if limit > 0 and used >= 0.9 * limit:
            self.status_var.set("⚠️ Token usage nearing limit!")
        else:
            self.status_var.set(f"Token usage refreshed: {used}/{limit}")

        # Throttle refresh button
        self.view.refresh_btn.configure(state="disabled")
        self.view.frame.after(
            2000, lambda: self.view.refresh_btn.configure(state="normal")
        )

    def save_model_settings(self):
        # Gather inputs
        model = self.view.model_entry.get().strip()
        try:
            temp = float(self.view.temp_slider.get())
            tokens = int(self.view.token_entry.get().strip())
        except ValueError:
            self.status_var.set("❌ Invalid input: temperature or tokens")
            return

        # Update config
        self.config.MODEL = model
        self.config.TEMPERATURE = temp
        self.config.MAX_TOKENS = tokens
        if hasattr(self.config, "save"):
            self.config.save()

        # Propagate to AI engine
        if hasattr(self.ai, "update_config"):
            self.ai.update_config(model=model, temperature=temp, max_tokens=tokens)

        self.status_var.set("✅ AI model settings saved.")
