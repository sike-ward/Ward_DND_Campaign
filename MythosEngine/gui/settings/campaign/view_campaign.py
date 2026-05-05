from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from MythosEngine.gui.widgets import GlowButton, SectionHeader


class CampaignSettingsView(QWidget):
    save_clicked = pyqtSignal()

    def __init__(self, parent, config):
        super().__init__(parent)
        self.config = config

        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 36, 40, 32)
        layout.setSpacing(24)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # ── Header ────────────────────────────────────────────────────────────
        header = SectionHeader("📚  Campaign Settings", "Configure your vault path and campaign-level API key.")
        layout.addWidget(header)

        # ── Vault ─────────────────────────────────────────────────────────────
        vault_group = QGroupBox("Vault Location")
        vault_layout = QFormLayout(vault_group)
        vault_layout.setSpacing(12)
        vault_layout.setContentsMargins(16, 16, 16, 16)

        vault_row = QHBoxLayout()
        vault_row.setSpacing(8)
        self.input_vault = QLineEdit()
        self.input_vault.setPlaceholderText("Path to your campaign vault folder...")
        self.input_vault.setMinimumHeight(36)
        vault_row.addWidget(self.input_vault)

        btn_browse = QPushButton("Browse")
        btn_browse.setProperty("secondary", "true")
        btn_browse.setFixedWidth(80)
        btn_browse.setMinimumHeight(36)
        btn_browse.clicked.connect(self._browse_vault)
        vault_row.addWidget(btn_browse)

        vault_layout.addRow("Vault Path:", vault_row)
        layout.addWidget(vault_group)

        # ── API Key ───────────────────────────────────────────────────────────
        api_group = QGroupBox("Campaign API Key")
        api_layout = QFormLayout(api_group)
        api_layout.setSpacing(12)
        api_layout.setContentsMargins(16, 16, 16, 16)

        self.input_api = QLineEdit()
        self.input_api.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_api.setPlaceholderText("Optional override key for this campaign")
        self.input_api.setMinimumHeight(36)
        api_layout.addRow("API Key:", self.input_api)

        layout.addWidget(api_group)

        # ── Save + Status ─────────────────────────────────────────────────────
        btn_row = QHBoxLayout()
        self.btn_save = GlowButton("Save Campaign Settings", "primary")
        self.btn_save.setMinimumHeight(38)
        self.btn_save.setFixedWidth(215)
        self.btn_save.clicked.connect(self.save_clicked.emit)
        btn_row.addWidget(self.btn_save)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        self.status_label = QLabel("")
        self.status_label.setProperty("role", "muted")
        layout.addWidget(self.status_label)

        layout.addStretch()

    # ── Helpers ───────────────────────────────────────────────────────────────
    def _browse_vault(self):
        path = QFileDialog.getExistingDirectory(self, "Select Vault Folder", self.input_vault.text() or "")
        if path:
            self.input_vault.setText(path)

    # ── Controller interface ──────────────────────────────────────────────────
    def get_vault_path(self):
        return self.input_vault.text()

    def set_vault_path(self, path):
        self.input_vault.setText(path)

    def get_api_key(self):
        return self.input_api.text()

    def set_api_key(self, key):
        self.input_api.setText(key)

    def set_status(self, text, error=False):
        color = "#EF4444" if error else "#10B981"
        self.status_label.setStyleSheet(f"color: {color}; font-size: 9pt; background: transparent;")
        self.status_label.setText(text)
