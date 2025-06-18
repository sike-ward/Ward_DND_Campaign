from PyQt6.QtCore import QObject
from PyQt6.QtWidgets import QInputDialog, QMessageBox

from Ward_DND_AI.utils.crash_handler import catch_and_report_crashes


class TimelineController(QObject):
    def __init__(self, view, ai_engine, storage_backend, config, status_var=None):
        super().__init__()
        self.view = view
        self.ai = ai_engine
        self.storage = storage_backend
        self.config = config
        self.status_var = status_var

        self.events = []
        self._refresh_event_list()

        self.view.add_btn.clicked.connect(catch_and_report_crashes(self.add_event))
        self.view.edit_btn.clicked.connect(catch_and_report_crashes(self.edit_event))
        self.view.delete_btn.clicked.connect(
            catch_and_report_crashes(self.delete_event)
        )

    def _refresh_event_list(self):
        self.view.event_list.clear()
        for ev in self.events:
            self.view.event_list.append(ev)

    @catch_and_report_crashes
    def add_event(self):
        text, ok = QInputDialog.getText(self.view, "New Event", "Event description:")
        if ok and text:
            self.events.append(text)
            self._refresh_event_list()

    @catch_and_report_crashes
    def edit_event(self):
        cursor = self.view.event_list.textCursor()
        current_text = cursor.selectedText()
        if not current_text:
            QMessageBox.warning(self.view, "Edit Event", "Select text to edit.")
            return

        text, ok = QInputDialog.getText(
            self.view, "Edit Event", "Event description:", text=current_text
        )
        if ok and text:
            # Replace selected text with new text
            cursor.insertText(text)
            # Update events list to reflect the change
            self.events = self.view.event_list.toPlainText().split("\n")

    @catch_and_report_crashes
    def delete_event(self):
        cursor = self.view.event_list.textCursor()
        selected_text = cursor.selectedText()
        if not selected_text:
            QMessageBox.warning(self.view, "Delete Event", "Select text to delete.")
            return

        confirm = QMessageBox.question(
            self.view,
            "Delete Event",
            f"Remove selected event?\n\n{selected_text}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if confirm == QMessageBox.StandardButton.Yes:
            # Remove selected text
            cursor.removeSelectedText()
            # Update events list accordingly
            self.events = self.view.event_list.toPlainText().split("\n")
