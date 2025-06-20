from PyQt6.QtCore import QObject


class DashboardController(QObject):
    def __init__(self, view, ai_engine, storage_backend, config, status_var=None):
        super().__init__()
        self.view = view
        self.ai_engine = ai_engine
        self.storage = storage_backend
        self.config = config
        self.status_var = status_var
        # TODO: connect any dashboard-specific signals here
