import os

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QListWidget,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from Ward_DND_AI.utils.utils import get_all_folders


class BrowseView(QWidget):
    def __init__(self, parent, config):
        super().__init__(parent)
        self.config = config

        # --- Main Layout ---
        main_layout = QVBoxLayout(self)

        # --- Top bar: Folder filter, New, Import ---
        top = QFrame(self)
        top_layout = QHBoxLayout(top)
        self.folder_menu = QComboBox()
        top_layout.addWidget(self.folder_menu)
        self.new_btn = QPushButton("New")
        self.import_btn = QPushButton("Import")
        top_layout.addWidget(self.new_btn)
        top_layout.addWidget(self.import_btn)
        main_layout.addWidget(top)

        # --- Body Layout: Left (notes), Right (preview + controls) ---
        body = QFrame(self)
        body_layout = QHBoxLayout(body)

        # Left pane: note list
        left = QFrame(body)
        left_layout = QVBoxLayout(left)
        self.notes_listbox = QListWidget()
        left_layout.addWidget(self.notes_listbox)
        body_layout.addWidget(left, 1)

        # Right pane: preview + buttons
        right = QFrame(body)
        right_layout = QVBoxLayout(right)

        ctrl = QFrame(right)
        ctrl_layout = QHBoxLayout(ctrl)
        self.edit_btn = QPushButton("Edit")
        self.save_btn = QPushButton("Save")
        self.cancel_btn = QPushButton("Cancel")
        self.toggle_btn = QPushButton("HTML View")
        for b in (self.edit_btn, self.save_btn, self.cancel_btn, self.toggle_btn):
            ctrl_layout.addWidget(b)
        right_layout.addWidget(ctrl)

        # Preview container (for controller to populate)
        self.preview_container = QFrame(right)
        self.preview_container_layout = QVBoxLayout(self.preview_container)
        right_layout.addWidget(self.preview_container, 1)

        # For controller compatibility (initially None)
        self.text_preview = None
        self.html_preview = None

        body_layout.addWidget(right, 3)
        main_layout.addWidget(body, 1)

        # --- Bottom status ---
        self.status_label = QLabel("")
        main_layout.addWidget(self.status_label)

    # Interface implementations for controller calls

    def clear_folders(self):
        self.folder_menu.clear()

    def add_folders(self, folders):
        self.folder_menu.addItems(folders)

    def clear_notes(self):
        self.notes_listbox.clear()

    def add_note(self, note_name):
        self.notes_listbox.addItem(note_name)

    def get_current_folder(self):
        return self.folder_menu.currentText()

    def get_selected_note_name(self):
        selected_items = self.notes_listbox.selectedItems()
        if not selected_items:
            return None
        return selected_items[0].text()

    def clear_preview(self):
        # Remove all widgets in preview container
        while self.preview_container_layout.count():
            item = self.preview_container_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        self.text_preview = None
        self.html_preview = None

    def set_text_preview(self, content, editable):
        self.clear_preview()
        self.text_preview = QTextEdit()
        self.text_preview.setReadOnly(not editable)
        self.text_preview.setPlainText(content)
        self.preview_container_layout.addWidget(self.text_preview)

    def set_html_preview(self, html):
        self.clear_preview()
        from PyQt6.QtWidgets import QLabel

        label = QLabel()
        label.setTextFormat(Qt.TextFormat.RichText)
        label.setText(html)
        label.setWordWrap(True)
        self.preview_container_layout.addWidget(label)
        self.html_preview = label

    def set_preview_mode_text(self):
        # For controller tracking, nothing special needed here
        pass

    def set_preview_mode_html(self):
        # For controller tracking, nothing special needed here
        pass

    def get_preview_mode(self):
        # This state should be managed by controller, so default text
        return "text"

    def set_toggle_button_text(self, text):
        self.toggle_btn.setText(text)

    def enable_buttons(self, save, cancel, edit):
        self.save_btn.setEnabled(save)
        self.cancel_btn.setEnabled(cancel)
        self.edit_btn.setEnabled(edit)

    def show_status(self, message):
        self.status_label.setText(message)

    def ask_user_folder(self, title, label):
        return QInputDialog.getItem(
            self, title, label, get_all_folders(self.config.VAULT_PATH), 0, False
        )

    def ask_user_filename(self, title, label):
        return QInputDialog.getText(self, title, label)

    def show_warning(self, title, message):
        QMessageBox.warning(self, title, message)

    def show_error(self, title, message):
        QMessageBox.critical(self, title, message)

    def ask_user_files(self, title, filter):
        files, _ = QFileDialog.getOpenFileNames(self, title, "", filter)
        return files

    def ask_user_save_path(self, title, default, filter):
        path, _ = QFileDialog.getSaveFileName(self, title, default, filter)
        return path

    def ask_user_confirm(self, title, message):
        reply = QMessageBox.question(
            self,
            title,
            message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        return reply == QMessageBox.StandardButton.Yes

    def open_external_path(self, path):
        import subprocess

        if os.name == "nt":
            os.startfile(path)
        else:
            subprocess.Popen(["xdg-open", path])

    def open_obsidian_link(self, vault, file_encoded):
        import subprocess

        uri = f"obsidian://open?vault={vault}&file={file_encoded}"
        if os.name == "nt":
            subprocess.Popen(["start", "", uri], shell=True)
        else:
            subprocess.Popen(["xdg-open", uri])
