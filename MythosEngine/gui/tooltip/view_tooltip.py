from PyQt6.QtCore import QPoint, Qt, QTimer
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget


class ToolTip(QWidget):
    def __init__(self, parent=None, text=""):
        super().__init__(parent, Qt.WindowType.ToolTip)
        self.text = text
        self.label = QLabel(text, self)
        self.label.setStyleSheet(
            """
            background-color: #1D1D28;
            color: #E8EAF0;
            border: none;
            border-radius: 6px;
            padding: 6px 10px;
            font-family: "Segoe UI";
            font-size: 9pt;
        """
        )
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.label)

        self.hide_timer = QTimer(self)
        self.hide_timer.setSingleShot(True)
        self.hide_timer.timeout.connect(self.hide)

    def show_tip(self, pos: QPoint, timeout=3000):
        self.move(pos)
        self.show()
        self.raise_()
        self.hide_timer.start(timeout)

    def hide_tip(self):
        self.hide()
