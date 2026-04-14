from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QPushButton,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class DebugView(QWidget):
    # Signals for Crash Logs tab
    refresh_crash_logs = pyqtSignal()
    crash_log_selected = pyqtSignal(int)
    copy_log = pyqtSignal()
    open_log_folder = pyqtSignal()
    delete_log = pyqtSignal()
    send_log = pyqtSignal()
    load_runtime_log = pyqtSignal()
    clear_runtime_log = pyqtSignal()
    copy_runtime_log = pyqtSignal()
    save_runtime_log = pyqtSignal()
    open_log_folder_runtime = pyqtSignal()

    # Runtime log tab signals can be added as needed

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs, 1)

        # ----- Crash Logs Tab -----
        crash_tab = QWidget()
        crash_layout = QVBoxLayout(crash_tab)
        crash_layout.setSpacing(8)

        # Log file list
        list_row = QHBoxLayout()
        self.crash_log_list = QListWidget()
        self.crash_log_list.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.crash_log_list.setFixedWidth(240)
        list_row.addWidget(self.crash_log_list, 0)

        # Log contents viewer
        self.crash_log_viewer = QTextEdit()
        self.crash_log_viewer.setReadOnly(True)
        self.crash_log_viewer.setFontFamily("Consolas")
        list_row.addWidget(self.crash_log_viewer, 1)
        crash_layout.addLayout(list_row, 3)

        # Button bar
        btn_row = QHBoxLayout()
        self.refresh_btn = QPushButton("Refresh")
        self.copy_btn = QPushButton("Copy")
        self.open_folder_btn = QPushButton("Open Folder")
        self.delete_btn = QPushButton("Delete")
        self.send_btn = QPushButton("Send")
        btn_row.addWidget(self.refresh_btn)
        btn_row.addWidget(self.copy_btn)
        btn_row.addWidget(self.open_folder_btn)
        btn_row.addWidget(self.delete_btn)
        btn_row.addWidget(self.send_btn)
        btn_row.addStretch(1)
        crash_layout.addLayout(btn_row)

        # Status line
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: gray; font-size: 10pt;")
        crash_layout.addWidget(self.status_label)

        self.tabs.addTab(crash_tab, "Crash Logs")

        # ----- Runtime Log Tab -----
        runtime_tab = QWidget()
        runtime_layout = QVBoxLayout(runtime_tab)
        runtime_layout.setSpacing(8)

        self.runtime_log_viewer = QTextEdit()
        self.runtime_log_viewer.setReadOnly(True)
        self.runtime_log_viewer.setFontFamily("Consolas")
        runtime_layout.addWidget(self.runtime_log_viewer, 1)

        # --- Runtime Log Controls ---
        runtime_btn_row = QHBoxLayout()
        self.runtime_refresh_btn = QPushButton("Reload")
        self.runtime_clear_btn = QPushButton("Clear")
        self.runtime_copy_btn = QPushButton("Copy")
        self.runtime_save_btn = QPushButton("Save")
        self.runtime_open_folder_btn = QPushButton("Open Folder")
        runtime_btn_row.addWidget(self.runtime_refresh_btn)
        runtime_btn_row.addWidget(self.runtime_clear_btn)
        runtime_btn_row.addWidget(self.runtime_copy_btn)
        runtime_btn_row.addWidget(self.runtime_save_btn)
        runtime_btn_row.addWidget(self.runtime_open_folder_btn)
        runtime_btn_row.addStretch(1)
        runtime_layout.addLayout(runtime_btn_row)

        self.tabs.addTab(runtime_tab, "Runtime Log")
        self.tabs.currentChanged.connect(self._on_tab_changed)

        # ---- Signal Wiring ----
        self.refresh_btn.clicked.connect(self.refresh_crash_logs.emit)
        self.crash_log_list.currentRowChanged.connect(self.crash_log_selected.emit)
        self.copy_btn.clicked.connect(self.copy_log.emit)
        self.open_folder_btn.clicked.connect(self.open_log_folder.emit)
        self.delete_btn.clicked.connect(self.delete_log.emit)
        self.send_btn.clicked.connect(self.send_log.emit)
        self.runtime_save_btn.clicked.connect(self.save_runtime_log.emit)
        self.runtime_refresh_btn.clicked.connect(self.load_runtime_log.emit)
        self.runtime_clear_btn.clicked.connect(self.clear_runtime_log.emit)
        self.runtime_copy_btn.clicked.connect(self.copy_runtime_log.emit)
        self.runtime_open_folder_btn.clicked.connect(self.open_log_folder_runtime.emit)
        # Krita-like style tweaks
        self.crash_log_list.setStyleSheet("font-size: 11pt;")
        self.crash_log_viewer.setStyleSheet(
            "font-size: 11pt; background: #282828; color: #dcdcdc; border: 1px solid #444;"
        )
        self.runtime_log_viewer.setStyleSheet(
            "font-size: 11pt; background: #232629; color: #e3e3e3; border: 1px solid #444;"
        )
        self.tabs.setStyleSheet("QTabBar::tab { min-width: 100px; padding: 6px; font-weight: bold; }")

    # --- Slots called by controller ---

    def set_crash_log_list(self, files):
        """files: list of (basename, mtime) tuples"""
        from datetime import datetime

        self.crash_log_list.clear()
        for fname, mtime in files:
            dt = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M")
            self.crash_log_list.addItem(f"{fname}   [{dt}]")

    def set_crash_log_contents(self, text):
        self.crash_log_viewer.setPlainText(text)

    def copy_to_clipboard(self, text):
        from PyQt6.QtWidgets import QApplication

        QApplication.instance().clipboard().setText(text)

    def show_status_message(self, text):
        self.status_label.setText(text)

    # --- Runtime Log support stubs ---
    def set_runtime_log_contents(self, text):
        self.runtime_log_viewer.setPlainText(text)

    def _on_tab_changed(self, index):
        # If runtime log tab is at index 1, adjust if you reorder tabs
        if index == 1:
            self.load_runtime_log.emit()

    # (Add clear/save/filter slots as you expand)
