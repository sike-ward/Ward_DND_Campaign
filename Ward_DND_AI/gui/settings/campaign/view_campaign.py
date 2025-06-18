from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class CampaignSettingsView(QWidget):
    save_clicked = pyqtSignal()

    def __init__(self, parent, config):
        super().__init__(parent)
        self.config = config

        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # Vault Path
        vault_layout = QHBoxLayout()
        self.label_vault = QLabel("Vault Path:")
        self.input_vault = QLineEdit()
        vault_layout.addWidget(self.label_vault)
        vault_layout.addWidget(self.input_vault)
        layout.addLayout(vault_layout)

        # API Key
        api_layout = QHBoxLayout()
        self.label_api = QLabel("API Key:")
        self.input_api = QLineEdit()
        self.input_api.setEchoMode(QLineEdit.EchoMode.Password)
        api_layout.addWidget(self.label_api)
        api_layout.addWidget(self.input_api)
        layout.addLayout(api_layout)

        # Save Button
        self.btn_save = QPushButton("Save Settings")
        layout.addWidget(self.btn_save)

        # Status Label
        self.status_label = QLabel("")
        layout.addWidget(self.status_label)

        self.btn_save.clicked.connect(self.save_clicked.emit)

    # Convenience getters/setters for controller

    def get_vault_path(self):
        return self.input_vault.text()

    def set_vault_path(self, path):
        self.input_vault.setText(path)

    def get_api_key(self):
        return self.input_api.text()

    def set_api_key(self, key):
        self.input_api.setText(key)

    def set_status(self, text):
        self.status_label.setText(text)
