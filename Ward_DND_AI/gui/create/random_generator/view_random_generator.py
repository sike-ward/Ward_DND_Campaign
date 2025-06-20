from PyQt6.QtWidgets import (
    QComboBox,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class RandomGeneratorView(QWidget):
    def __init__(self, parent, config):
        super().__init__(parent)
        self.config = config

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        label_prompt = QLabel("Enter Prompt:")
        layout.addWidget(label_prompt)

        self.prompt_entry = QLineEdit()
        self.prompt_entry.setPlaceholderText("Type your prompt here")
        layout.addWidget(self.prompt_entry)

        label_type = QLabel("Select Tag/Type:")
        layout.addWidget(label_type)

        self.type_menu = QComboBox()
        self.type_menu.addItems(["..."])  # Populate later as needed
        self.type_menu.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        layout.addWidget(self.type_menu)

        self.generate_btn = QPushButton("Generate")
        layout.addWidget(self.generate_btn)

        self.save_btn = QPushButton("Save to Vault")
        layout.addWidget(self.save_btn)

        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setAcceptRichText(False)
        layout.addWidget(self.output_text, 1)  # Expand output text
