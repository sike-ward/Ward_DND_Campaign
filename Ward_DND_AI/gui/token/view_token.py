# Ward_DND_AI/gui/token/view_token.py


import customtkinter as ctk


class TokenView:
    def __init__(self, parent, config):
        self.config = config

        self.frame = ctk.CTkFrame(parent)
        self.frame.pack(fill="both", expand=True, padx=20, pady=20)

        # --- Session Token Usage Section ---
        usage_section = ctk.CTkFrame(self.frame)
        usage_section.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(
            usage_section, text="Session Token Usage", font=("Segoe UI", 14)
        ).pack(anchor="w", pady=(0, 4))

        self.usage_label = ctk.CTkLabel(
            usage_section, text="Loading...", font=("Consolas", 12)
        )
        self.usage_label.pack(anchor="w")

        self.refresh_btn = ctk.CTkButton(usage_section, text="Refresh Token Info")
        self.refresh_btn.pack(anchor="w", pady=(8, 0))

        # --- AI Model Settings Section ---
        settings_section = ctk.CTkFrame(self.frame)
        settings_section.pack(fill="x")

        ctk.CTkLabel(
            settings_section, text="AI Model Settings", font=("Segoe UI", 14)
        ).pack(anchor="w", pady=(0, 8))

        # Model Name
        row1 = ctk.CTkFrame(settings_section)
        row1.pack(fill="x", pady=4)
        ctk.CTkLabel(row1, text="Model Name:", width=100).pack(side="left")
        self.model_entry = ctk.CTkEntry(row1)
        self.model_entry.pack(side="left", fill="x", expand=True)

        # Temperature
        row2 = ctk.CTkFrame(settings_section)
        row2.pack(fill="x", pady=4)
        ctk.CTkLabel(row2, text="Temperature:", width=100).pack(side="left")
        self.temp_slider = ctk.CTkSlider(row2, from_=0.0, to=1.5, number_of_steps=30)
        self.temp_slider.pack(side="left", fill="x", expand=True)

        # Max Tokens
        row3 = ctk.CTkFrame(settings_section)
        row3.pack(fill="x", pady=4)
        ctk.CTkLabel(row3, text="Max Tokens:", width=100).pack(side="left")
        self.token_entry = ctk.CTkEntry(row3)
        self.token_entry.pack(side="left", fill="x", expand=True)

        # Save Button
        self.save_btn = ctk.CTkButton(settings_section, text="Save Model Settings")
        self.save_btn.pack(pady=(10, 0))
