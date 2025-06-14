import customtkinter as ctk


class RandomGeneratorView:
    def __init__(self, parent):
        self.frame = ctk.CTkFrame(parent)
        self.frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Prompt entry
        ctk.CTkLabel(self.frame, text="Enter Prompt:").pack(anchor="w")
        self.prompt_entry = ctk.CTkEntry(self.frame)
        self.prompt_entry.pack(fill="x", pady=(0, 10))

        # Generation type (from tags)
        ctk.CTkLabel(self.frame, text="Select Tag/Type:").pack(anchor="w")
        self.type_menu = ctk.CTkOptionMenu(self.frame, values=["..."])
        self.type_menu.pack(fill="x", pady=(0, 10))

        # Generate and Save buttons
        self.generate_btn = ctk.CTkButton(self.frame, text="Generate")
        self.generate_btn.pack(pady=(0, 10))

        self.save_btn = ctk.CTkButton(self.frame, text="Save to Vault")
        self.save_btn.pack(pady=(0, 10))

        # Output box
        self.output_text = ctk.CTkTextbox(self.frame, wrap="word")
        self.output_text.pack(fill="both", expand=True, pady=(10, 0))
        self.output_text.configure(state="disabled")
