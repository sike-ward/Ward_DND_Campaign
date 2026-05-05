from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from MythosEngine.gui.widgets import GlowButton, SectionHeader


class AISettingsView(QWidget):
    save_clicked = pyqtSignal()

    def __init__(self, parent, ctx):
        super().__init__(parent)
        self.ctx = ctx
        self.config = ctx.config
        self.ai_engine = ctx.ai

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(scroll.Shape.NoFrame)
        root.addWidget(scroll)

        container = QWidget()
        scroll.setWidget(container)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(40, 36, 40, 32)
        layout.setSpacing(24)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # ── Header ────────────────────────────────────────────────────────────
        header = SectionHeader("✦  AI Settings", "Configure your AI provider, models, and token limits.")
        layout.addWidget(header)

        # ── API Key ───────────────────────────────────────────────────────────
        api_group = QGroupBox("API Key")
        api_layout = QFormLayout(api_group)
        api_layout.setSpacing(12)
        api_layout.setContentsMargins(16, 16, 16, 16)

        key_row = QHBoxLayout()
        key_row.setSpacing(8)
        self.input_api_key = QLineEdit()
        self.input_api_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_api_key.setPlaceholderText("sk-...")
        self.input_api_key.setMinimumHeight(36)
        key_row.addWidget(self.input_api_key)

        self.btn_show_key = QPushButton("Show")
        self.btn_show_key.setProperty("secondary", "true")
        self.btn_show_key.setFixedWidth(64)
        self.btn_show_key.setMinimumHeight(36)
        self.btn_show_key.setCheckable(True)
        self.btn_show_key.toggled.connect(self._toggle_key_visibility)
        key_row.addWidget(self.btn_show_key)

        api_layout.addRow("OpenAI API Key:", key_row)
        layout.addWidget(api_group)

        # ── Models ────────────────────────────────────────────────────────────
        model_group = QGroupBox("Model Selection")
        model_layout = QFormLayout(model_group)
        model_layout.setSpacing(12)
        model_layout.setContentsMargins(16, 16, 16, 16)

        self.combo_completion_model = QComboBox()
        self.combo_completion_model.addItems(
            [
                "gpt-4o",
                "gpt-4o-mini",
                "gpt-4-turbo",
                "gpt-3.5-turbo",
            ]
        )
        self.combo_completion_model.setMinimumHeight(36)
        model_layout.addRow("Completion Model:", self.combo_completion_model)

        self.combo_embedding_model = QComboBox()
        self.combo_embedding_model.addItems(
            [
                "text-embedding-3-small",
                "text-embedding-3-large",
            ]
        )
        self.combo_embedding_model.setMinimumHeight(36)
        model_layout.addRow("Embedding Model:", self.combo_embedding_model)

        layout.addWidget(model_group)

        # ── Tokens ────────────────────────────────────────────────────────────
        token_group = QGroupBox("Token Limits")
        token_layout = QFormLayout(token_group)
        token_layout.setSpacing(12)
        token_layout.setContentsMargins(16, 16, 16, 16)

        self.input_max_tokens = QLineEdit()
        self.input_max_tokens.setPlaceholderText("e.g. 4000")
        self.input_max_tokens.setMinimumHeight(36)
        token_layout.addRow("Max Tokens:", self.input_max_tokens)

        self.label_token_usage = QLabel("Tokens used: 0 / 0")
        self.label_token_usage.setProperty("role", "muted")
        token_layout.addRow("Usage:", self.label_token_usage)

        layout.addWidget(token_group)

        # ── Save button ───────────────────────────────────────────────────────
        btn_row = QHBoxLayout()
        self.btn_save = GlowButton("Save AI Settings", "primary")
        self.btn_save.setMinimumHeight(38)
        self.btn_save.setFixedWidth(180)
        self.btn_save.clicked.connect(self.save_clicked.emit)
        btn_row.addWidget(self.btn_save)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        layout.addStretch()

    # ── Helpers ───────────────────────────────────────────────────────────────
    def _toggle_key_visibility(self, visible: bool):
        self.input_api_key.setEchoMode(QLineEdit.EchoMode.Normal if visible else QLineEdit.EchoMode.Password)
        self.btn_show_key.setText("Hide" if visible else "Show")

    # ── Controller interface ──────────────────────────────────────────────────
    def get_api_key(self):
        return self.input_api_key.text()

    def set_api_key(self, key):
        self.input_api_key.setText(key)

    def get_embedding_model(self):
        return self.combo_embedding_model.currentText()

    def set_embedding_model(self, model):
        idx = self.combo_embedding_model.findText(model)
        if idx >= 0:
            self.combo_embedding_model.setCurrentIndex(idx)

    def get_completion_model(self):
        return self.combo_completion_model.currentText()

    def set_completion_model(self, model):
        idx = self.combo_completion_model.findText(model)
        if idx >= 0:
            self.combo_completion_model.setCurrentIndex(idx)

    def get_max_tokens(self):
        try:
            return int(self.input_max_tokens.text())
        except ValueError:
            return 4000

    def set_max_tokens(self, max_tokens):
        self.input_max_tokens.setText(str(max_tokens))

    def set_token_usage(self, used, max_tokens):
        self.label_token_usage.setText(f"Tokens used: {used:,} / {max_tokens:,}")
