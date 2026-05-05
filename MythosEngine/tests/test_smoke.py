import unittest
from unittest.mock import Mock

from MythosEngine.gui.gui import LoreMainApp
from MythosEngine.storage.storage_base import StorageBackend


class SmokeTest(unittest.TestCase):
    def test_app_starts(self):
        try:
            # Mock the storage backend with all required methods
            storage_mock = Mock(spec=StorageBackend)
            storage_mock.list_all_notes.return_value = ["lore/note1.md"]
            storage_mock.read_note.return_value = ("Mock Note Title", "Mock note body")
            storage_mock.list_tags.return_value = ["tag1", "tag2"]
            storage_mock.list_folders.return_value = ["folder1", "folder2"]

            # Mock the AI engine with required ask() method
            ai_mock = Mock()
            ai_mock.ask.return_value = ("Mock AI response", 10, 20)

            # Start and immediately destroy the app to validate startup
            app = LoreMainApp(ai_engine=ai_mock, storage_backend=storage_mock)
            app.destroy()
        except Exception as e:
            self.fail(f"App failed to start: {e}")
