from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget


class DashboardView(QWidget):
    def __init__(self, parent, config):
        super().__init__(parent)
        self.config = config

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.addWidget(QLabel("📊 Dashboard (WIP)"))
