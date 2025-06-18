import sys
import traceback
from functools import wraps

from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
)


def handle_crash(exc_type, exc_value, exc_traceback):
    trace = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    error_msg = f"{exc_type.__name__}: {exc_value}"
    print("!!! CRASH HANDLER CALLED !!!")
    print(trace)

    app = QApplication.instance() or QApplication(sys.argv)  # noqa: F841
    dlg = CrashDialogQt(error_msg, trace)
    dlg.exec()


class CrashDialogQt(QDialog):
    def __init__(self, error_message, traceback_text):
        super().__init__()
        self.setWindowTitle("Obsidian Lore Assistant - Crash Handler")
        self.resize(820, 500)

        layout = QVBoxLayout(self)

        # Header
        label = QLabel("<b>Application Crash Detected</b>")
        label.setStyleSheet("font-size: 17px; color: #b94a48;")
        layout.addWidget(label)

        # Summary/Error box
        layout.addWidget(QLabel("Summary:"))
        summary = QTextEdit()
        summary.setReadOnly(True)
        summary.setPlainText(error_message)
        summary.setStyleSheet("background: #f9e2e2; color: #7c2121; font-weight: bold;")
        summary.setFixedHeight(54)
        layout.addWidget(summary)

        # Traceback
        layout.addWidget(QLabel("Traceback:"))
        tracebox = QTextEdit()
        tracebox.setReadOnly(True)
        tracebox.setPlainText(traceback_text)
        tracebox.setStyleSheet(
            "background: #23242a; color: #e0e0e0; font-family: Consolas;"
        )
        layout.addWidget(tracebox)

        # Button row (copy, close)
        btns = QHBoxLayout()
        copy_btn = QPushButton("Copy Report")
        close_btn = QPushButton("Close")
        btns.addWidget(copy_btn)
        btns.addWidget(close_btn)
        layout.addLayout(btns)

        copy_btn.clicked.connect(
            lambda: self.copy_to_clipboard(error_message, traceback_text)
        )
        close_btn.clicked.connect(self.accept)

    def copy_to_clipboard(self, error_message, traceback_text):
        clipboard = QApplication.clipboard()
        clipboard.setText(f"{error_message}\n\n{traceback_text}")


def catch_and_report_crashes(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except Exception:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            handle_crash(exc_type, exc_value, exc_traceback)

    return wrapper
