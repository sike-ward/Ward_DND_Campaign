import customtkinter as ctk


class SummarizeView:
    def __init__(self, parent):
        self.frame = ctk.CTkFrame(parent)
        self.frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Folder selection
        ctk.CTkLabel(
            self.frame, text="Folder to Summarize:", font=("Segoe UI", 12)
        ).pack(anchor="w")
        self.folder_menu = ctk.CTkOptionMenu(self.frame, values=["..."])
        self.folder_menu.pack(fill="x", pady=(0, 10))

        # Style selection
        ctk.CTkLabel(self.frame, text="Style:", font=("Segoe UI", 12)).pack(anchor="w")
        self.style_menu = ctk.CTkOptionMenu(
            self.frame, values=["brief", "bullet points", "detailed"]
        )
        self.style_menu.pack(fill="x", pady=(0, 10))
        self.style_menu.set("brief")

        # Summarize button
        self.summarize_btn = ctk.CTkButton(self.frame, text="Summarize Notes")
        self.summarize_btn.pack(pady=(0, 10))

        # Output
        ctk.CTkLabel(self.frame, text="Summary Output:", font=("Segoe UI", 12)).pack(
            anchor="w", pady=(10, 2)
        )
        self.output_text = ctk.CTkTextbox(self.frame, wrap="word")
        self.output_text.pack(fill="both", expand=True)
        self.output_text.configure(state="disabled")
