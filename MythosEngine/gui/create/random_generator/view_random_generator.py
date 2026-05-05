from PyQt6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QSizePolicy,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from MythosEngine.gui.widgets import GlowButton


class RandomGeneratorView(QWidget):
    def __init__(self, parent, config):
        super().__init__(parent)
        self.config = config

        layout = QVBoxLayout(self)
        layout.setContentsMargins(36, 32, 36, 28)
        layout.setSpacing(18)

        label_prompt = QLabel("Enter Prompt:")
        label_prompt.setProperty("role", "muted")
        layout.addWidget(label_prompt)

        self.prompt_entry = QLineEdit()
        self.prompt_entry.setPlaceholderText("Type your prompt here...")
        self.prompt_entry.setMinimumHeight(42)
        layout.addWidget(self.prompt_entry)

        label_type = QLabel("Select Tag/Type:")
        label_type.setProperty("role", "muted")
        layout.addWidget(label_type)

        self.type_menu = QComboBox()
        self.type_menu.addItems(["..."])  # Populate later as needed
        self.type_menu.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.type_menu.setMinimumHeight(40)
        layout.addWidget(self.type_menu)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)

        self.generate_btn = GlowButton("Generate", "primary")
        self.generate_btn.setMinimumHeight(42)
        self.generate_btn.setFixedWidth(160)
        btn_row.addWidget(self.generate_btn)

        self.save_btn = GlowButton("Save to Vault", "secondary")
        self.save_btn.setMinimumHeight(42)
        self.save_btn.setFixedWidth(160)
        btn_row.addWidget(self.save_btn)

        btn_row.addStretch()
        layout.addLayout(btn_row)

        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setAcceptRichText(False)
        self.output_text.setProperty("readonly", "true")
        layout.addWidget(self.output_text, 1)
