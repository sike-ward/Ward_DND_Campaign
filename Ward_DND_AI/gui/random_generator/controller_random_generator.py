import tkinter as tk


class RandomGeneratorController:
    def __init__(self, view, ai, storage, config, status_var=None):
        self.view = view
        self.ai = ai
        self.storage = storage
        self.config = config
        self.status_var = status_var or tk.StringVar()

        self.view.generate_btn.configure(command=self.on_generate)

    def on_generate(self):
        prompt = self.view.prompt_entry.get().strip()
        if not prompt:
            self._show_output("[Please enter a prompt]")
            return

        # Call your AI engine's random generate method
        result = self.ai.generate_random(prompt)

        self._show_output(result)

    def _show_output(self, text: str):
        self.view.output_text.configure(state="normal")
        self.view.output_text.delete("1.0", "end")
        self.view.output_text.insert("1.0", text)
        self.view.output_text.configure(state="disabled")
