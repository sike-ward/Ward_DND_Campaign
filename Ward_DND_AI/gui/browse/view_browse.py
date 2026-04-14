import os

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QComboBox,
    QCompleter,
    QDialog,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QListWidget,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QTabWidget,
    QTextBrowser,
    QTextEdit,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from Ward_DND_AI.config.config import load_note_templates


class SplitNoteEditor(QWidget):
    """
    Shows a markdown editor on left and a rendered preview on right.
    """

    def __init__(self, note_name, markdown_content, read_only=False):
        super().__init__()
        self.note_name = note_name
        self._markdown_content = markdown_content

        layout = QHBoxLayout(self)
        self.editor = QTextEdit()
        self.editor.setPlainText(markdown_content)
        self.preview = QTextBrowser()
        self.preview.setOpenExternalLinks(True)
        self.update_preview()
        layout.addWidget(self.editor, 1)
        layout.addWidget(self.preview, 1)
        self.editor.setReadOnly(read_only)

        self.editor.textChanged.connect(self.update_preview if not read_only else lambda: None)

    def update_preview(self):
        import markdown2

        html = markdown2.markdown(self.editor.toPlainText())
        self.preview.setHtml(html)

    def toPlainText(self):
        return self.editor.toPlainText()


class NotesTree(QTreeWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.controller = None  # Will be set by BrowseView after construction

    def dropEvent(self, event):
        # Get dragged items
        selected_items = self.selectedItems()
        if not selected_items:
            super().dropEvent(event)
            return

        # Get drop target
        target_item = self.itemAt(event.position().toPoint())
        target_folder = ""
        if target_item and hasattr(target_item, "folder_path"):
            target_folder = target_item.folder_path
        elif target_item and hasattr(target_item, "note_path"):
            parent = target_item.parent()
            if parent and hasattr(parent, "folder_path"):
                target_folder = parent.folder_path
            else:
                target_folder = ""
        else:
            target_folder = ""

        moved_any = False
        error_msgs = []

        for item in selected_items:
            # Moving notes
            if hasattr(item, "note_path"):
                note_path = item.note_path
                filename = os.path.basename(note_path)
                new_path = f"{target_folder}/{filename}" if target_folder else filename

                # Prevent overwrite without confirmation
                if note_path != new_path:
                    if (
                        self.controller
                        and hasattr(self.controller, "storage")
                        and self.controller.storage.exists(new_path)
                    ):
                        confirm = QMessageBox.question(
                            self,
                            "Overwrite Note",
                            f"Note '{filename}' already exists in '{target_folder}'. Overwrite?",
                            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                        )
                        if confirm != QMessageBox.StandardButton.Yes:
                            continue

                    try:
                        self.controller.storage.move_note(note_path, new_path)
                        self.controller.move_undo_stack.append(("note", new_path, note_path))
                        moved_any = True
                        self.controller.v.rename_tab_by_note(note_path, new_path)
                        self.controller.v.show_status(f"Moved note: {note_path} → {new_path}")
                    except Exception as e:
                        error_msgs.append(f"Failed to move note: {note_path}: {e}")

            # Moving folders
            elif hasattr(item, "folder_path") and not hasattr(item, "note_path"):
                folder_path = item.folder_path
                if not folder_path or folder_path == target_folder:
                    continue

                # Prevent illegal moves (folder into itself or descendant)
                if target_folder.startswith(folder_path):
                    QMessageBox.warning(
                        self,
                        "Invalid Move",
                        "Cannot move a folder into itself or its subfolder.",
                    )
                    continue

                new_path = (
                    f"{target_folder}/{os.path.basename(folder_path)}"
                    if target_folder
                    else os.path.basename(folder_path)
                )

                # Prevent overwrite without confirmation
                if (
                    self.controller
                    and hasattr(self.controller, "storage")
                    and self.controller.storage.folder_exists(new_path)
                ):
                    confirm = QMessageBox.question(
                        self,
                        "Overwrite Folder",
                        f"Folder '{os.path.basename(folder_path)}' already exists in '{target_folder}'. Overwrite?",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    )
                    if confirm != QMessageBox.StandardButton.Yes:
                        continue

                try:
                    self.controller.storage.move_folder(folder_path, new_path)
                    self.controller.move_undo_stack.append(("folder", new_path, folder_path))
                    moved_any = True
                    self.controller.v.show_status(f"Moved folder: {folder_path} → {new_path}")
                except Exception as e:
                    error_msgs.append(f"Failed to move folder: {folder_path}: {e}")

        super().dropEvent(event)

        if moved_any and self.controller:
            self.controller.load_tree()
        if error_msgs:
            QMessageBox.critical(self, "Move Errors", "\n".join(error_msgs))

        super().dropEvent(event)
        if moved_any and self.controller:
            self.controller.load_tree()


class BrowseView(QWidget):
    def __init__(self, parent, config):
        super().__init__(parent)
        self.config = config

        # --- Main Layout ---
        main_layout = QVBoxLayout(self)

        # --- Top Bar ---
        top = QFrame(self)
        top_layout = QHBoxLayout(top)
        self.folder_menu = QComboBox()
        top_layout.addWidget(QLabel("Folder:"))
        top_layout.addWidget(self.folder_menu)

        self.tag_filter = QLineEdit()
        self.tag_filter.setPlaceholderText("Tag(s), comma-separated or leave blank for all")
        self.tag_completer = QCompleter([])
        self.tag_completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.tag_completer.setFilterMode(Qt.MatchFlag.MatchContains)

        self.tag_filter.setCompleter(self.tag_completer)
        self.tag_filter.textEdited.connect(lambda: self.tag_completer.complete())

        top_layout.addWidget(QLabel("Tag:"))
        top_layout.addWidget(self.tag_filter)
        self.tag_logic = QComboBox()
        self.tag_logic.addItems(["AND", "OR"])
        top_layout.addWidget(self.tag_logic)

        self.template_dropdown = QComboBox()
        self.templates_dict = load_note_templates()
        self.template_dropdown.addItems(list(self.templates_dict.keys()))
        top_layout.addWidget(QLabel("Template:"))
        top_layout.addWidget(self.template_dropdown)
        self.create_btn = QPushButton("Create")
        top_layout.addWidget(self.create_btn)
        self.template_desc = QLabel("")
        self.template_desc.setStyleSheet("color: gray; font-size: 10pt;")
        top_layout.addWidget(self.template_desc)
        self.template_dropdown.currentTextChanged.connect(self._update_template_desc)
        self._update_template_desc(self.template_dropdown.currentText())

        self.import_btn = QPushButton("Import")
        top_layout.addWidget(self.import_btn)
        self.export_btn = QPushButton("Export")
        top_layout.addWidget(self.export_btn)
        self.delete_btn = QPushButton("Delete")
        top_layout.addWidget(self.delete_btn)
        self.tag_btn = QPushButton("Tag")
        top_layout.addWidget(self.tag_btn)
        self.move_btn = QPushButton("Move")
        top_layout.addWidget(self.move_btn)
        self.undo_move_btn = QPushButton("Undo")
        self.star_btn = QPushButton("★ Favorite")
        top_layout.addWidget(self.star_btn)

        top_layout.addWidget(self.undo_move_btn)
        self.fav_filter_cb = QCheckBox("Show Only Favorites")
        top_layout.addWidget(self.fav_filter_cb)
        main_layout.addWidget(top)

        # --- Search Bar Row (below top bar, above multiselect/notes tree) ---
        search_row = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search notes...")
        self.search_type = QComboBox()
        self.search_type.addItems(["Title", "Tag", "Within"])
        self.search_btn = QPushButton("Search")
        self.clear_search_btn = QPushButton("Clear")
        search_row.addWidget(self.search_input)
        search_row.addWidget(self.search_type)
        search_row.addWidget(self.search_btn)
        search_row.addWidget(self.clear_search_btn)
        main_layout.addLayout(search_row)
        self.search_completer = QCompleter([])
        self.search_completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.search_completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self.search_input.setCompleter(self.search_completer)
        self.search_input.textEdited.connect(lambda: self.search_completer.complete())

        # --- Body: Left (notes), Right (preview + controls) ---
        body = QFrame(self)
        body_layout = QHBoxLayout(body)

        # Left pane: custom note tree
        left = QFrame(body)
        left_layout = QVBoxLayout(left)

        self.multi_select_cb = QCheckBox("Enable Multi-select")
        left_layout.addWidget(self.multi_select_cb)

        self.select_btn = QPushButton("Select")
        self.select_btn.setVisible(False)
        left_layout.addWidget(self.select_btn)

        self.notes_tree = NotesTree()
        self.notes_tree.setHeaderHidden(True)
        self.notes_tree.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.notes_tree.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        left_layout.addWidget(self.notes_tree)
        body_layout.addWidget(left, 1)
        self.notes_tree.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.notes_tree.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.notes_tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)

        # Right pane
        right = QFrame(body)
        right_layout = QVBoxLayout(right)

        ctrl = QFrame(right)
        ctrl_layout = QHBoxLayout(ctrl)

        self.edit_btn = QPushButton("Edit")
        self.edit_btn.setMinimumHeight(28)
        ctrl_layout.addWidget(self.edit_btn)

        self.save_btn = QPushButton("Save")
        self.save_btn.setMinimumHeight(28)
        ctrl_layout.addWidget(self.save_btn)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setMinimumHeight(28)
        ctrl_layout.addWidget(self.cancel_btn)

        self.summarize_btn = QPushButton("Summarize")
        self.summarize_btn.setMinimumHeight(28)
        ctrl_layout.addWidget(self.summarize_btn)

        self.history_btn = QPushButton("History")
        ctrl_layout.addWidget(self.history_btn)

        self.links_btn = QPushButton("Links")
        ctrl_layout.addWidget(self.links_btn)

        self.metadata_btn = QPushButton("Metadata")
        ctrl_layout.addWidget(self.metadata_btn)

        self.show_source_btn = QPushButton("Show Markdown Source")
        self.show_source_btn.setMinimumHeight(28)
        self.show_source_btn.setVisible(False)
        ctrl_layout.addWidget(self.show_source_btn)

        ctrl_layout.setContentsMargins(0, 4, 0, 4)
        ctrl_layout.setSpacing(8)
        right_layout.addWidget(ctrl)

        self.preview_tabs = QTabWidget(right)
        self.preview_tabs.setTabsClosable(True)
        self.preview_tabs.tabCloseRequested.connect(self._on_tab_close_requested)
        self.preview_tabs.currentChanged.connect(self._on_tab_changed)
        right_layout.addWidget(self.preview_tabs, 1)

        self.metadata_label = QLabel("")
        self.metadata_label.setTextFormat(Qt.TextFormat.RichText)
        self.metadata_label.setWordWrap(True)
        self.metadata_label.setMinimumHeight(30)
        self.metadata_label.setMaximumHeight(600)  # or whatever looks right for your layout

        meta_scroll = QScrollArea()
        meta_scroll.setWidgetResizable(True)
        meta_scroll.setWidget(self.metadata_label)
        meta_scroll.setFixedHeight(60)  # matches max height above

        right_layout.addWidget(meta_scroll)

        body_layout.addWidget(right, 3)
        main_layout.addWidget(body, 1)

        self.status_label = QLabel()
        main_layout.addWidget(self.status_label)
        self.tag_filter.returnPressed.connect(lambda: self.controller.load_tree())
        self.tag_logic.currentTextChanged.connect(lambda: self.controller.load_tree())

        self.notes_tree.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.toggle_multi_select(self.multi_select_cb.isChecked())
        self.status_label.setText("Ready")

    # --- View <-> Controller interface ---

    def clear_folders(self):
        self.folder_menu.clear()

    def add_folders(self, folders):
        self.folder_menu.addItems(folders)

    def get_current_folder(self):
        return self.folder_menu.currentText()

    def clear_notes(self):
        self.notes_tree.clear()
        self.show_metadata("")
        self.show_status("Select a note to view details.")

    def add_note(self, note_name):
        item = QTreeWidgetItem([note_name])
        self.notes_tree.addTopLevelItem(item)

    def clear_preview(self):
        while self.preview_tabs.count() > 0:
            self.preview_tabs.removeTab(0)

    def show_metadata(self, note_name):
        print("show_metadata called with:", note_name)  # Debug
        # Defensive: Only show full metadata for files with .md extension
        # (If you want to allow .txt, add: or note_name.lower().endswith(".txt"))
        if not note_name or "<b>" in note_name or not note_name.lower().endswith(".md"):
            self.metadata_label.setText("")  # Clear for folders or non-note nodes
            return
        try:
            meta = self.controller.get_full_metadata(note_name)
            if not meta or "File Name" not in meta:  # Defensive
                self.metadata_label.setText(f"<b>File:</b> {note_name}<br>(No metadata)")
                return
            lines = []
            for k, v in meta.items():
                lines.append(f"<b>{k}:</b> {v}")
            self.metadata_label.setText("<br>".join(lines))
        except Exception as e:
            self.metadata_label.setText(f"<b>File:</b> {note_name}<br>(metadata unavailable: {e})")

    def enable_buttons(self, save=False, cancel=False, edit=True):
        self.save_btn.setEnabled(save)
        self.cancel_btn.setEnabled(cancel)
        self.edit_btn.setEnabled(edit)

    def show_status(self, message):
        self.status_label.setText(message)

    def ask_user_folder(self, title, label):
        return QInputDialog.getItem(self, title, label, self._get_all_folders(), 0, False)

    def _get_all_folders(self):
        # Always fetch from storage backend, never direct FS
        folders = {""}
        if hasattr(self, "controller") and hasattr(self.controller, "storage"):
            for f in self.controller.storage.list_folders():
                folders.add(f)
        return sorted(list(folders))

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

    def open_note_tab(self, note_name, content, editable=False):
        """
        Open the note in its own tab if not already open.
        If already open, switch to it.
        """
        # Check if tab is already open for this note
        for i in range(self.preview_tabs.count()):
            widget = self.preview_tabs.widget(i)
            if hasattr(widget, "note_name") and widget.note_name == note_name:
                self.preview_tabs.setCurrentIndex(i)
                # Optionally update content
                if editable and hasattr(widget, "editor"):
                    widget.editor.setPlainText(content)
                elif not editable and hasattr(widget, "setHtml"):
                    import markdown2

                    widget.setHtml(markdown2.markdown(content))
                return widget

        # If not open, create new tab
        if not editable:
            import markdown2
            from PyQt6.QtWidgets import QTextBrowser

            widget = QTextBrowser()
            html = markdown2.markdown(content)
            widget.setHtml(html)
        else:
            import markdown2
            from PyQt6.QtWidgets import QTextEdit

            widget = QTextEdit()
            widget.setAcceptRichText(True)
            widget.setHtml(markdown2.markdown(content))
            widget._markdown_content = content
        widget.note_name = note_name
        self.preview_tabs.addTab(widget, os.path.basename(note_name))
        self.preview_tabs.setCurrentWidget(widget)
        return widget

    def close_current_tab(self):
        idx = self.preview_tabs.currentIndex()
        if idx >= 0:
            self.preview_tabs.removeTab(idx)

    def close_tab_by_name(self, note_name):
        for i in range(self.preview_tabs.count()):
            if self.preview_tabs.tabText(i) == note_name:
                self.preview_tabs.removeTab(i)
                return

    def get_open_tab_names(self):
        return [self.preview_tabs.tabText(i) for i in range(self.preview_tabs.count())]

    def _on_tab_changed(self, idx):
        editor = self.preview_tabs.widget(idx)
        if editor and hasattr(editor, "editor") and not editor.editor.isReadOnly():
            self.enable_buttons(save=True, cancel=True, edit=False)
        else:
            self.enable_buttons(save=False, cancel=False, edit=True)

    def _on_tab_close_requested(self, idx):
        editor = self.preview_tabs.widget(idx)
        if hasattr(editor, "dirty") and editor.dirty:
            reply = QMessageBox.question(
                self,
                "Unsaved Changes",
                f"Save changes to '{editor.note_name}' before closing?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel,
            )
            if reply == QMessageBox.StandardButton.Cancel:
                return
            elif reply == QMessageBox.StandardButton.Yes:
                if hasattr(self, "controller"):
                    self.controller.save_note_from_editor(editor)
        self.preview_tabs.removeTab(idx)
        if self.preview_tabs.count() == 0:
            self.show_metadata("")

    def show_markdown_preview(self, note_name, markdown_content):
        import markdown2
        from PyQt6.QtWidgets import QTextBrowser

        html = markdown2.markdown(markdown_content)

        # Remove any open tab for this note
        for i in range(self.preview_tabs.count()):
            widget = self.preview_tabs.widget(i)
            if hasattr(widget, "note_name") and widget.note_name == note_name:
                self.preview_tabs.removeTab(i)
                break

        # Create new preview tab
        preview = QTextBrowser()
        preview.setHtml(html)
        preview.note_name = note_name
        preview.setReadOnly(True)
        self.preview_tabs.addTab(preview, os.path.basename(note_name))
        self.preview_tabs.setCurrentWidget(preview)

    def show_html_editor(self, note_name, html_content):
        from PyQt6.QtWidgets import QHBoxLayout, QTextBrowser, QTextEdit, QWidget

        # Remove any existing tab for this note
        for i in range(self.preview_tabs.count()):
            if getattr(self.preview_tabs.widget(i), "note_name", None) == note_name:
                self.preview_tabs.removeTab(i)
                break

        # Side-by-side: raw HTML editor and live HTML preview
        widget = QWidget()
        layout = QHBoxLayout(widget)
        editor = QTextEdit()
        editor.setPlainText(html_content)
        preview = QTextBrowser()
        preview.setHtml(html_content)
        preview.setOpenExternalLinks(True)
        layout.addWidget(editor, 1)
        layout.addWidget(preview, 1)
        widget.note_name = note_name

        # Optional: live preview update for HTML
        def update_preview():
            preview.setHtml(editor.toPlainText())

        editor.textChanged.connect(update_preview)

        self.preview_tabs.addTab(widget, os.path.basename(note_name) + " (HTML Editing)")
        self.preview_tabs.setCurrentWidget(widget)

    def show_markdown_editor(self, note_name, markdown_content):
        # Check if tab for this note is already open in edit mode
        for i in range(self.preview_tabs.count()):
            widget = self.preview_tabs.widget(i)
            if hasattr(widget, "note_name") and widget.note_name == note_name:
                self.preview_tabs.setCurrentIndex(i)
                return

        # Always use SplitNoteEditor for editing
        widget = SplitNoteEditor(note_name, markdown_content, read_only=False)
        widget.note_name = note_name
        self.preview_tabs.addTab(widget, os.path.basename(note_name) + " (Editing)")
        self.preview_tabs.setCurrentWidget(widget)

    # --------- For legacy multi-select/checkbox API ----------

    def toggle_multi_select(self, enabled):
        if enabled:
            self.notes_tree.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
            self.select_btn.setVisible(True)
            self.undo_move_btn.setVisible(True)
        else:
            self.notes_tree.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
            self.select_btn.setVisible(False)
            self.undo_move_btn.setVisible(False)

    def get_selected_note_name(self):
        items = self.notes_tree.selectedItems()
        if not items:
            return None
        item = items[0]
        # If it's a folder, ignore; if it's a note, get its full path
        if hasattr(item, "note_path"):
            return item.note_path
        return None

    def set_tree_data(self, folders, notes, current_folder, current_tag, multi_select_enabled):
        self.notes_tree.clear()
        # Build all folder nodes first, in order from root downward
        folder_items = {}
        all_folders = set([""] + folders)
        # Sort so parents are created before children (by depth then name)
        for folder_path in sorted(all_folders, key=lambda x: (x.count("/"), x.replace("\\", "/"))):
            # Filter by current_folder (if any)
            if current_folder and not (folder_path == current_folder or folder_path.startswith(current_folder + "\\")):
                continue
            name = folder_path if folder_path else "<root>"
            item = QTreeWidgetItem([name])
            item.folder_path = folder_path
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsDropEnabled)
            folder_items[folder_path] = item

        # Parent folders into tree
        for folder_path, item in folder_items.items():
            parent_path = os.path.dirname(folder_path)
            if parent_path in folder_items and folder_path != "":
                folder_items[parent_path].addChild(item)
            elif folder_path == "":
                self.notes_tree.addTopLevelItem(item)

        # Add notes under their correct folder nodes
        for note in notes:
            folder_path = os.path.dirname(note)
            # Tag filtering...
            # (existing tag filtering logic here)

            # Favorite filter:
            if hasattr(self, "fav_filter_cb") and self.fav_filter_cb.isChecked():
                if not (
                    hasattr(self, "controller")
                    and hasattr(self.controller, "is_note_starred")
                    and self.controller.is_note_starred(note)
                ):
                    continue

            starred = False
            if hasattr(self, "controller") and hasattr(self.controller, "is_note_starred"):
                starred = self.controller.is_note_starred(note)
            display_name = f"★ {os.path.basename(note)}" if starred else os.path.basename(note)
            note_item = QTreeWidgetItem([display_name])
            note_item.note_path = note
            note_item.display_name = display_name

            folder_item = folder_items.get(folder_path, None)
            if folder_item:
                folder_item.addChild(note_item)
            else:
                folder_items[""].addChild(note_item)

        self.notes_tree.expandAll()
        self.show_status("Select a note to view details.")

    def rename_tab_by_note(self, old_path, new_path):
        for i in range(self.preview_tabs.count()):
            widget = self.preview_tabs.widget(i)
            if getattr(widget, "note_name", None) == old_path:
                widget.note_name = new_path
                self.preview_tabs.setTabText(i, os.path.basename(new_path))

    def _update_template_desc(self, template_key):
        desc = self.templates_dict.get(template_key, {}).get("description", "")
        self.template_desc.setText(desc)

    def _on_tab_changed(self, idx):
        widget = self.preview_tabs.widget(idx)
        if widget and hasattr(widget, "note_name"):
            self.show_metadata(widget.note_name)
        else:
            self.metadata_label.setText("")  # Or whatever you want for empty

    def _open_quick_switcher(self):
        # Collect all notes
        note_names = []
        if hasattr(self.controller, "storage"):
            note_names = list(self.controller.storage.list_all_notes())
        dlg = QuickSwitcherDialog(self, note_names)
        if dlg.exec():
            sel = dlg.get_selected_note()
            if sel:
                content = self.controller.storage.read_note(sel)
                self.open_note_tab(sel, content, editable=False)
                self.show_metadata(sel)

    def update_tag_completer(self, tags):
        # tags: a list or set of tag strings
        self.tag_completer.model().setStringList(list(tags))

    def update_search_completer(self, note_names):
        # note_names: list of all note filenames (not full paths, just the visible names)
        self.search_completer.model().setStringList([os.path.basename(n) for n in note_names])

    def save_all_unsaved_tabs_to_recovery_folder(self, recovery_dir):
        """
        Save all open note tabs (editors only) to recovery folder.
        """
        import os
        from datetime import datetime

        for i in range(self.preview_tabs.count()):
            widget = self.preview_tabs.widget(i)
            # Only care about tabs that are editors, not just previewers
            # (QTextEdit, SplitNoteEditor, etc.)
            if hasattr(widget, "note_name"):
                note_name = widget.note_name
                # Try to get markdown/text content
                if hasattr(widget, "toPlainText"):
                    content = widget.toPlainText()
                elif hasattr(widget, "editor") and hasattr(widget.editor, "toPlainText"):
                    content = widget.editor.toPlainText()
                else:
                    continue
                # Save to file
                safe_name = note_name.replace("/", "__").replace("\\", "__")
                fname = f"recovery_{safe_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
                path = os.path.join(recovery_dir, fname)
                with open(path, "w", encoding="utf-8") as f:
                    f.write(content)


class NoteLinksDialog(QDialog):
    def __init__(self, parent, note_name, forward_links, backlinks, open_callback):
        super().__init__(parent)
        self.setWindowTitle(f"Links – {os.path.basename(note_name)}")
        self.resize(600, 400)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<b>Forward Links:</b> (links in this note)"))
        self.fw_list = QListWidget()
        for note in sorted(forward_links):
            self.fw_list.addItem(note)
        layout.addWidget(self.fw_list)
        layout.addWidget(QLabel("<b>Backlinks:</b> (notes linking to this note)"))
        self.bw_list = QListWidget()
        for note in sorted(backlinks):
            self.bw_list.addItem(note)
        layout.addWidget(self.bw_list)
        self.fw_list.itemDoubleClicked.connect(lambda item: self._open(item, open_callback))
        self.bw_list.itemDoubleClicked.connect(lambda item: self._open(item, open_callback))

    def _open(self, item, cb):
        cb(item.text())
        self.accept()


from PyQt6.QtWidgets import QDialog


class VersionHistoryDialog(QDialog):
    def __init__(self, parent, versions, note_path, restore_callback):
        super().__init__(parent)
        self.versions = versions
        self.setWindowTitle(f"Version History - {os.path.basename(note_path)}")
        self.resize(600, 400)
        layout = QVBoxLayout(self)
        self.list = QListWidget()
        for vfile, vtime in versions:
            self.list.addItem(f"{vtime} – {os.path.basename(vfile)}")
        layout.addWidget(QLabel("Double-click to preview. Select and Restore to roll back."))
        layout.addWidget(self.list)
        self.restore_btn = QPushButton("Restore Selected")
        layout.addWidget(self.restore_btn)
        self.selected_file = None

        def restore():
            idx = self.list.currentRow()
            if idx < 0:
                return
            self.selected_file = versions[idx][0]
            self.accept()

        self.restore_btn.clicked.connect(restore)

        self.list.itemDoubleClicked.connect(self.preview_version)

    def preview_version(self, item):
        idx = self.list.currentRow()
        vfile = self.selected_file = self.versions[idx][0]
        with open(vfile, encoding="utf-8") as f:
            text = f.read()
        import markdown2
        from PyQt6.QtWidgets import QTextBrowser

        dlg = QDialog(self)
        dlg.setWindowTitle("Preview Version (HTML)")
        layout = QVBoxLayout(dlg)
        tb = QTextBrowser()
        tb.setOpenExternalLinks(True)
        html = markdown2.markdown(text)
        tb.setHtml(html)
        layout.addWidget(tb)
        dlg.resize(600, 600)
        dlg.exec()


from PyQt6.QtWidgets import (
    QDialog,
    QListWidgetItem,
)


class QuickSwitcherDialog(QDialog):
    def __init__(self, parent, note_names):
        super().__init__(parent)
        self.setWindowTitle("Quick Switch (Go to Note)")
        self.resize(400, 400)
        layout = QVBoxLayout(self)
        self.input = QLineEdit(self)
        self.input.setPlaceholderText("Type to search...")
        layout.addWidget(self.input)
        self.list = QListWidget(self)
        self.all_notes = note_names
        self.filtered = []
        layout.addWidget(self.list)

        self.input.textChanged.connect(self.filter_notes)
        self.list.itemDoubleClicked.connect(self.accept)

        self.input.setFocus()
        self.filter_notes("")

    def filter_notes(self, text):
        self.list.clear()
        text = text.lower()
        self.filtered = [n for n in self.all_notes if text in os.path.basename(n).lower()]
        for n in self.filtered:
            item = QListWidgetItem(os.path.basename(n))
            item.setData(256, n)  # 256 = Qt.UserRole, full path
            self.list.addItem(item)

    def get_selected_note(self):
        items = self.list.selectedItems()
        if items:
            return items[0].data(256)
        elif self.list.count() > 0:
            return self.list.item(0).data(256)
        return None

    def keyPressEvent(self, event):
        from PyQt6.QtCore import Qt

        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self.accept()
        elif event.key() == Qt.Key.Key_Escape:
            self.reject()
        else:
            super().keyPressEvent(event)


from PyQt6.QtWidgets import (
    QDialog,
    QWidget,
)


class MetadataEditorDialog(QDialog):
    def __init__(self, parent, metadata_dict):
        super().__init__(parent)
        self.setWindowTitle("Edit Metadata")
        self.resize(400, 300)
        self.layout = QVBoxLayout(self)
        self.fields = {}  # key: (QLineEdit, QLineEdit)

        # Existing fields
        for k, v in metadata_dict.items():
            self.add_field_row(str(k), str(v))

        # Button row
        btn_row = QHBoxLayout()
        self.add_btn = QPushButton("Add Field")
        self.save_btn = QPushButton("Save")
        self.cancel_btn = QPushButton("Cancel")
        btn_row.addWidget(self.add_btn)
        btn_row.addWidget(self.save_btn)
        btn_row.addWidget(self.cancel_btn)
        self.layout.addLayout(btn_row)

        self.add_btn.clicked.connect(self.add_field_row)
        self.save_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)

    def add_field_row(self, key="", value="", *args, **kwargs):
        # Accepts any arguments; ignores those passed by signal
        row = QHBoxLayout()
        k_edit = QLineEdit(str(key))
        v_edit = QLineEdit(str(value))
        rm_btn = QPushButton("Remove")
        row.addWidget(QLabel("Key:"))
        row.addWidget(k_edit)
        row.addWidget(QLabel("Value:"))
        row.addWidget(v_edit)
        row.addWidget(rm_btn)
        container = QWidget()
        container.setLayout(row)
        self.layout.insertWidget(self.layout.count() - 1, container)
        self.fields[k_edit] = (v_edit, container)

        def remove_row():
            self.layout.removeWidget(container)
            container.deleteLater()
            del self.fields[k_edit]

        rm_btn.clicked.connect(remove_row)

    def get_metadata(self):
        meta = {}
        for k_edit, (v_edit, _) in self.fields.items():
            key = k_edit.text().strip()
            val = v_edit.text().strip()
            if key:
                meta[key] = val
        return meta
