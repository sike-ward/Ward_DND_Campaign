from PyQt6.QtCore import QEvent, QObject
from PyQt6.QtGui import QCursor

from Ward_DND_AI.gui.tooltip import ToolTip


class ToolTipController(QObject):
    def __init__(self, parent_widget, tooltip_text=""):
        super().__init__(parent_widget)
        self.parent_widget = parent_widget
        self.tooltip = ToolTip(parent_widget, tooltip_text)
        self.parent_widget.installEventFilter(self)

    def eventFilter(self, obj, event):
        if obj == self.parent_widget:
            if event.type() == QEvent.Type.Enter:
                global_pos = QCursor.pos()
                self.tooltip.show_tip(global_pos)
            elif event.type() == QEvent.Type.Leave:
                self.tooltip.hide_tip()
        return super().eventFilter(obj, event)

    def set_tooltip_text(self, text):
        self.tooltip.label.setText(text)
