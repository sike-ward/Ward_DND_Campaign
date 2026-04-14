from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


class DashboardView(QWidget):
    def __init__(self, parent, config):
        super().__init__(parent)
        self.config = config
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        # ── Title ──────────────────────────────────────────────────────
        title = QLabel("Dashboard")
        title.setStyleSheet("font-size: 20pt; font-weight: bold;")
        root.addWidget(title)

        # ── Stats row ──────────────────────────────────────────────────
        stats_row = QHBoxLayout()
        stats_row.setSpacing(12)

        self.stat_notes = self._stat_card("Notes", "—")
        self.stat_folders = self._stat_card("Folders", "—")
        self.stat_characters = self._stat_card("Characters", "—")
        self.stat_sessions = self._stat_card("Sessions", "—")

        for card in (self.stat_notes, self.stat_folders, self.stat_characters, self.stat_sessions):
            stats_row.addWidget(card)

        root.addLayout(stats_row)

        # ── Recent Notes ───────────────────────────────────────────────
        recent_box = QGroupBox("Recent Notes")
        recent_layout = QVBoxLayout(recent_box)
        self.recent_list = QListWidget()
        self.recent_list.setMaximumHeight(180)
        recent_layout.addWidget(self.recent_list)
        root.addWidget(recent_box)

        # ── Quick actions ──────────────────────────────────────────────
        actions_box = QGroupBox("Quick Actions")
        actions_layout = QHBoxLayout(actions_box)

        self.btn_new_note = QPushButton("New Note")
        self.btn_browse = QPushButton("Browse Vault")
        self.btn_ask_ai = QPushButton("Ask AI")
        self.btn_refresh = QPushButton("Refresh")

        for btn in (self.btn_new_note, self.btn_browse, self.btn_ask_ai, self.btn_refresh):
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            actions_layout.addWidget(btn)

        root.addWidget(actions_box)

        # ── Status label ───────────────────────────────────────────────
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: gray; font-size: 9pt;")
        root.addWidget(self.status_label)

        root.addStretch()

    def _stat_card(self, label: str, value: str) -> QFrame:
        frame = QFrame()
        frame.setFrameShape(QFrame.Shape.StyledPanel)
        frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        layout = QVBoxLayout(frame)
        layout.setSpacing(2)

        val_label = QLabel(value)
        val_label.setStyleSheet("font-size: 24pt; font-weight: bold;")
        val_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        lbl = QLabel(label)
        lbl.setStyleSheet("font-size: 9pt; color: gray;")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(val_label)
        layout.addWidget(lbl)

        # Store reference to the value label for easy updates
        frame._value_label = val_label
        return frame

    def set_stat(self, card: QFrame, value: str):
        card._value_label.setText(value)
