from PyQt6.QtWidgets import QTabWidget, QVBoxLayout, QWidget

from Ward_DND_AI.gui.create.random_generator.view_random_generator import (
    RandomGeneratorView,
)


class CreateView(QWidget):
    def __init__(self, parent, config):
        super().__init__(parent)
        self.config = config

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # Sub-tabs for Create
        self.subtabs = QTabWidget()
        # Random Generator sub-tab
        self.random_view = RandomGeneratorView(self.subtabs, config)
        self.subtabs.addTab(self.random_view, "Random Gen")
        # TODO: self.subtabs.addTab(..., "Map Maker"), etc.

        layout.addWidget(self.subtabs)
