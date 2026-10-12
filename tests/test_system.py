from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from docusort.ui.main_window import MainWindow


class MemorySettings:
    def __init__(self, *_args):
        self.values = {}

    def value(self, key, default_value=None, type=None):
        value = self.values.get(key, default_value)
        return type(value) if type is not None else value

    def setValue(self, key, value):
        self.values[key] = value

    def remove(self, key):
        self.values.pop(key, None)

    def sync(self):
        pass


class MainWindowSystemTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_source_recursion_toggle_updates_visible_files(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            source = root / "source"
            target = root / "target"
            nested = source / "nested"
            nested.mkdir(parents=True)
            target.mkdir()
            (source / "root.pdf").write_text("root")
            nested_file = nested / "nested.pdf"
            nested_file.write_text("nested")

            settings = MemorySettings()
            settings.setValue("source_directory", str(source))
            settings.setValue("target_directory", str(target))
            with patch("docusort.ui.main_window.QSettings", return_value=settings):
                window = MainWindow()
                try:
                    self.assertFalse(window.recursive_source_checkbox.isChecked())
                    self.assertEqual(window.file_list.count(), 1)

                    window.recursive_source_checkbox.setChecked(True)

                    self.assertEqual(window.file_list.count(), 2)
                    nested_item = next(
                        window.file_list.item(index)
                        for index in range(window.file_list.count())
                        if Path(window.file_list.item(index).data(Qt.ItemDataRole.UserRole)) == nested_file
                    )
                    window.on_file_selected(nested_item)
                    self.assertEqual(window.current_file, nested_file)

                    window.recursive_source_checkbox.setChecked(False)

                    self.assertEqual(window.file_list.count(), 1)
                    self.assertIsNone(window.current_file)
                    self.assertFalse(settings.value("recursive_source_listing"))
                finally:
                    window.close()


if __name__ == "__main__":
    unittest.main()
