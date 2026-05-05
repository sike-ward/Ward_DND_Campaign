from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QSizePolicy,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from MythosEngine.gui.widgets import SectionHeader


class CollapsibleSection(QWidget):
    """Clean collapsible section — no border, uses background color separation."""

    def __init__(self, title, parent=None):
        super().__init__(parent)

        self.toggle_btn = QToolButton(text=f"  {title}", checkable=True, checked=False)
        self.toggle_btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.toggle_btn.setArrowType(Qt.ArrowType.RightArrow)
        self.toggle_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.toggle_btn.setMinimumHeight(40)

        self.content_widget = QWidget()
        self.content_widget.setVisible(False)

        self.toggle_btn.toggled.connect(self._on_toggled)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 4, 0, 4)
        layout.setSpacing(4)
        layout.addWidget(self.toggle_btn)
        layout.addWidget(self.content_widget)

    def setContentLayout(self, layout):
        layout.setContentsMargins(16, 8, 8, 8)
        self.content_widget.setLayout(layout)

    def _on_toggled(self, checked):
        self.content_widget.setVisible(checked)
        self.toggle_btn.setArrowType(Qt.ArrowType.DownArrow if checked else Qt.ArrowType.RightArrow)


class AppSettingsView(QWidget):
    def __init__(self, parent=None, config=None):
        super().__init__(parent)
        self.config = config
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 36, 40, 32)
        main_layout.setSpacing(20)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # ── Header ────────────────────────────────────────────────────────────
        header = SectionHeader("⚙  App Settings", "Appearance, behavior, and startup preferences.")
        main_layout.addWidget(header)

        # --- Appearance Section ---
        appearance_section = CollapsibleSection("Appearance")
        appearance_layout = QFormLayout()

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light", "Dark"])
        appearance_layout.addRow("Theme:", self.theme_combo)

        self.font_size_combo = QComboBox()
        self.font_size_combo.addItems(["Small", "Medium", "Large"])
        appearance_layout.addRow("Font Size:", self.font_size_combo)

        self.compact_mode_checkbox = QCheckBox("Enable Compact Mode")
        appearance_layout.addRow(self.compact_mode_checkbox)

        appearance_section.setContentLayout(appearance_layout)
        main_layout.addWidget(appearance_section)

        # --- Behavior Section ---
        behavior_section = CollapsibleSection("Behavior")
        behavior_layout = QFormLayout()

        self.tooltips_checkbox = QCheckBox("Show Tooltips")
        behavior_layout.addRow(self.tooltips_checkbox)

        self.startup_tab_combo = QComboBox()
        self.startup_tab_combo.addItems(["Dashboard", "AI", "Browse", "Create", "World"])
        behavior_layout.addRow("Startup Tab:", self.startup_tab_combo)

        behavior_section.setContentLayout(behavior_layout)
        main_layout.addWidget(behavior_section)

        # --- Placeholders for More Sections ---
        notifications_section = CollapsibleSection("Notifications (coming soon)")
        notifications_section.setContentLayout(QFormLayout())
        main_layout.addWidget(notifications_section)

        advanced_section = CollapsibleSection("Advanced (coming soon)")
        advanced_section.setContentLayout(QFormLayout())
        main_layout.addWidget(advanced_section)

        main_layout.addStretch()
