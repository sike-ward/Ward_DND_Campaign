from PyQt6.QtCore import QObject

from Ward_DND_AI.gui.create.random_generator.controller_random_generator import (
    RandomGeneratorController,
)


class CreateController(QObject):
    def __init__(self, view, ai_engine, storage, config, status_var=None):
        super().__init__()
        self.view = view
        self.ai_engine = ai_engine
        self.storage = storage
        self.config = config
        self.status_var = status_var

        # Hook up Random Generator inside Create
        self.random_ctrl = RandomGeneratorController(
            self.view.random_view, ai_engine, storage, config
        )
        # TODO: instantiate other sub-controllers here
