from PyQt6.QtCore import QPoint, Qt, QTimer
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget


class ToolTip(QWidget):
    def __init__(self, parent=None, text=""):
        super().__init__(parent, Qt.WindowType.ToolTip)
        self.text = text
        self.label = QLabel(text, self)
        self.label.setStyleSheet(
            """
            background-color: #23272e;
            color: #eee;
            border: 1px solid #555;
            padding: 3px 7px;
            font-family: "Segoe UI";
            font-size: 10pt;
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
