# MythosEngine/gui/chat/view_chat.py
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QTextBrowser,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from MythosEngine.gui.widgets import GlowButton, SectionHeader, ShadowCard


class ChatView(QWidget):
    def __init__(self, parent, config):
        super().__init__(parent)
        self.config = config
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(40, 36, 40, 32)
        root.setSpacing(20)

        # Header
        header = SectionHeader(
            "✦  AI Assistant",
            "Ask anything about your world, lore, or notes.",
        )
        root.addWidget(header)

        # Conversation history
        self.history_text = QTextBrowser()
        self.history_text.setOpenExternalLinks(False)
        root.addWidget(self.history_text, 3)

        # Output box
        output_label = QLabel("RESPONSE")
        output_label.setProperty("role", "muted")
        output_label.setStyleSheet("font-weight: 600; letter-spacing: 1.5px; font-size: 8pt;")
        root.addWidget(output_label)

        self.output_box = QTextEdit()
        self.output_box.setReadOnly(True)
        self.output_box.setProperty("readonly", "true")
        self.output_box.setMinimumHeight(100)
        self.output_box.setMaximumHeight(180)
        root.addWidget(self.output_box, 1)

        # Input area — elevated card
        input_card = ShadowCard(shadow_blur=16)
        input_layout = QVBoxLayout(input_card)
        input_layout.setContentsMargins(20, 16, 20, 16)
        input_layout.setSpacing(14)

        self.prompt_box = QTextEdit()
        self.prompt_box.setPlaceholderText("Ask about your world...")
        self.prompt_box.setFixedHeight(80)
        self.prompt_box.setStyleSheet(
            "QTextEdit { background: transparent; border: none; font-size: 10pt; padding: 0; }"
        )
        input_layout.addWidget(self.prompt_box)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        self.chat_btn = GlowButton("✦  Ask AI", "primary")
        self.chat_btn.setMinimumHeight(38)
        self.chat_btn.setFixedWidth(140)

        self.preview_btn = GlowButton("Preview", "secondary")
        self.preview_btn.setFixedWidth(90)
        self.preview_btn.setMinimumHeight(38)

        self.clear_btn = GlowButton("Clear", "ghost")
        self.clear_btn.setFixedWidth(80)
        self.clear_btn.setMinimumHeight(38)

        btn_row.addWidget(self.chat_btn)
        btn_row.addWidget(self.preview_btn)
        btn_row.addWidget(self.clear_btn)
        btn_row.addStretch()

        self.save_btn = GlowButton("Save Answer", "secondary")
        self.save_btn.setEnabled(False)
        self.save_btn.setFixedWidth(115)
        self.save_btn.setMinimumHeight(38)

        self.split_btn = GlowButton("Split & Save", "secondary")
        self.split_btn.setEnabled(False)
        self.split_btn.setFixedWidth(115)
        self.split_btn.setMinimumHeight(38)

        btn_row.addWidget(self.save_btn)
        btn_row.addWidget(self.split_btn)

        input_layout.addLayout(btn_row)
        root.addWidget(input_card)

        # Status
        self.status_label = QLabel("")
        self.status_label.setProperty("role", "muted")
        root.addWidget(self.status_label)

    def save_chat_state_to_recovery_folder(self, recovery_dir):
        from datetime import datetime
        from pathlib import Path as _Path

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        dest = _Path(recovery_dir) / f"recovery_chat_{timestamp}.txt"
        dest.parent.mkdir(parents=True, exist_ok=True)
        prompt = self.prompt_box.toPlainText()
        output = self.output_box.toPlainText()
        history = self.history_text.toPlainText()
        dest.write_text(
            f"# Chat Tab Crash Recovery\n\nPrompt:\n{prompt}\n\nOutput:\n{output}\n\nHistory:\n{history}\n",
            encoding="utf-8",
        )
