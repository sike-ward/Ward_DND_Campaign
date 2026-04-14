from PyQt6.QtCore import QObject
from PyQt6.QtWidgets import QInputDialog, QMessageBox

from Ward_DND_AI.utils.crash_handler import catch_and_report_crashes


class TimelineController(QObject):
    def __init__(self, view, ctx, status_var=None):
        super().__init__()
        self.view = view
        self.ctx = ctx
        self.ai = ctx.ai
        self.storage = ctx.storage
        self.config = ctx.config

        self.events = self._load()
        self._refresh_event_list()

        self.view.add_btn.clicked.connect(catch_and_report_crashes(self.add_event))
        self.view.edit_btn.clicked.connect(catch_and_report_crashes(self.edit_event))
        self.view.delete_btn.clicked.connect(catch_and_report_crashes(self.delete_event))

    # ── Persistence ────────────────────────────────────────────────────
    def _load(self) -> list:
        if self.storage and hasattr(self.storage, "read_timeline"):
            return self.storage.read_timeline()
        return []

    def _save(self):
        if self.storage and hasattr(self.storage, "save_timeline"):
            self.storage.save_timeline(self.events)

    # ── View sync ──────────────────────────────────────────────────────
    def _refresh_event_list(self):
        self.view.event_list.setReadOnly(False)
        self.view.event_list.setPlainText("\n".join(self.events))
        self.view.event_list.setReadOnly(True)

    # ── Actions ────────────────────────────────────────────────────────
    @catch_and_report_crashes
    def add_event(self):
        text, ok = QInputDialog.getText(self.view, "New Event", "Event description:")
        if ok and text.strip():
            self.events.append(text.strip())
            self._save()
            self._refresh_event_list()

    @catch_and_report_crashes
    def edit_event(self):
        if not self.events:
            QMessageBox.information(self.view, "Edit Event", "No events to edit.")
            return

        item, ok = QInputDialog.getItem(self.view, "Edit Event", "Select event to edit:", self.events, 0, False)
        if not ok:
            return

        idx = self.events.index(item)
        new_text, ok = QInputDialog.getText(self.view, "Edit Event", "Event description:", text=item)
        if ok and new_text.strip():
            self.events[idx] = new_text.strip()
            self._save()
            self._refresh_event_list()

    @catch_and_report_crashes
    def delete_event(self):
        if not self.events:
            QMessageBox.information(self.view, "Delete Event", "No events to delete.")
            return

        item, ok = QInputDialog.getItem(self.view, "Delete Event", "Select event to remove:", self.events, 0, False)
        if not ok:
            return

        confirm = QMessageBox.question(
            self.view,
            "Delete Event",
            f"Remove this event?\n\n{item}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if confirm == QMessageBox.StandardButton.Yes:
            self.events.remove(item)
            self._save()
            self._refresh_event_list()
