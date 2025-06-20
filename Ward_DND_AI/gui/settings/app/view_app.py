from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QGroupBox,
    QSizePolicy,
    QToolButton,
    QVBoxLayout,
    QWidget,
)


class CollapsibleSection(QGroupBox):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setTitle("")
        self.toggle_btn = QToolButton(text=title, checkable=True, checked=False)
        self.toggle_btn.setStyleSheet("font-weight: bold;")
        self.toggle_btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.toggle_btn.setArrowType(Qt.ArrowType.RightArrow)
        self.toggle_btn.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        self.content_widget = QWidget()
        self.content_widget.setVisible(False)

        self.toggle_btn.toggled.connect(self._on_toggled)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        layout.addWidget(self.toggle_btn)
        layout.addWidget(self.content_widget)

    def setContentLayout(self, layout):
        self.content_widget.setLayout(layout)

    def _on_toggled(self, checked):
        self.content_widget.setVisible(checked)
        self.toggle_btn.setArrowType(
            Qt.ArrowType.DownArrow if checked else Qt.ArrowType.RightArrow
        )


class AppSettingsView(QWidget):
    def __init__(self, parent=None, config=None):
        super().__init__(parent)
        self.config = config
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

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
        self.startup_tab_combo.addItems(
            ["Dashboard", "AI", "Browse", "Create", "World"]
        )
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
