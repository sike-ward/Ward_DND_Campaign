from PyQt6.QtCore import QObject

from Ward_DND_AI.utils.crash_handler import catch_and_report_crashes


class RandomGeneratorController(QObject):
    def __init__(self, view, ai_engine, storage_backend, config, status_var=None):
        super().__init__()
        self.view = view
        self.ai = ai_engine
        self.storage = storage_backend
        self.config = config
        self.status_var = status_var  # optional for status bar updates

        self.view.generate_btn.clicked.connect(
            catch_and_report_crashes(self.on_generate)
        )
        self.view.save_btn.clicked.connect(catch_and_report_crashes(self.on_save))

    @catch_and_report_crashes
    def on_generate(self):
        prompt = self.view.prompt_entry.text().strip()
        if not prompt:
            self._show_output("[Please enter a prompt]")
            return

        # Call your AI engine's random generate method
        result = self.ai.generate_random(prompt)
        self._show_output(result)

    @catch_and_report_crashes
    def on_save(self):
        # Implement your saving logic here
        self._show_output("[Save functionality not implemented yet]")

    def _show_output(self, text: str):
        self.view.output_text.setPlainText(text)
