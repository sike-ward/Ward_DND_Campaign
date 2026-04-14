from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class ChatView(QWidget):
    def __init__(self, parent, config):
        super().__init__(parent)
        self.config = config

        # --- Main layout ---
        main_layout = QVBoxLayout(self)

        # --- Prompt Input Row ---
        prompt_row = QHBoxLayout()
        self.prompt_box = QTextEdit()
        self.prompt_box.setFixedHeight(90)
        prompt_row.addWidget(self.prompt_box)
        self.preview_btn = QPushButton("Preview")
        prompt_row.addWidget(self.preview_btn)
        main_layout.addLayout(prompt_row)

        # --- Output Row ---
        output_row = QHBoxLayout()
        self.output_box = QTextEdit()
        self.output_box.setReadOnly(True)
        output_row.addWidget(self.output_box)

        # --- Buttons Panel ---
        button_panel = QVBoxLayout()
        self.chat_btn = QPushButton("Chat")
        self.save_btn = QPushButton("Save Answer")
        self.save_btn.setEnabled(False)
        self.split_btn = QPushButton("Split & Save")
        self.split_btn.setEnabled(False)
        self.clear_btn = QPushButton("Clear History")
        for b in (self.chat_btn, self.save_btn, self.split_btn, self.clear_btn):
            button_panel.addWidget(b)
        output_row.addLayout(button_panel)
        main_layout.addLayout(output_row)

        # --- History Box ---
        self.history_text = QTextEdit()
        self.history_text.setReadOnly(True)
        self.history_text.setFixedHeight(100)
        main_layout.addWidget(self.history_text)

        # --- Status Bar ---
        self.status_label = QLabel("")
        main_layout.addWidget(self.status_label)

    def save_chat_state_to_recovery_folder(self, recovery_dir):
        """
        Save current prompt, output, and history text to recovery folder.
        """
        import os
        from datetime import datetime

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        fname = f"recovery_chat_{timestamp}.txt"
        path = os.path.join(recovery_dir, fname)
        prompt = self.prompt_box.toPlainText()
        output = self.output_box.toPlainText()
        history = self.history_text.toPlainText()

        with open(path, "w", encoding="utf-8") as f:
            f.write("# Chat Tab Crash Recovery\n\n")
            f.write(f"Prompt:\n{prompt}\n\n")
            f.write(f"Output:\n{output}\n\n")
            f.write(f"History:\n{history}\n")
