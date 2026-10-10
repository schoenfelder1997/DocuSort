from pathlib import Path
import tempfile
import unittest

from docusort.core.file_service import FileService


class FileServiceTests(unittest.TestCase):
    def test_generate_target_name_with_date(self):
        name = FileService.generate_target_name(
            "2024-06-05",
            "Utilities",
            "Invoice",
            ".pdf",
            "YYYY-MM-dd",
        )
        self.assertEqual(name, "2024-06-05_Utilities_Invoice.pdf")

    def test_generate_target_name_without_date(self):
        name = FileService.generate_target_name(
            "2024-06-05",
            "Utilities",
            "Invoice",
            ".pdf",
            "None",
        )
        self.assertEqual(name, "Utilities_Invoice.pdf")

    def test_ensure_unique_destination_appends_suffix(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            directory = Path(temp_dir)
            (directory / "2024-06-05_Company_Invoice.pdf").write_text("content")

            target = FileService.ensure_unique_destination(directory, "2024-06-05_Company_Invoice.pdf")

            self.assertEqual(target.name, "2024-06-05_Company_Invoice_2.pdf")

    def test_list_files_includes_nested_files_in_relative_path_order(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            directory = Path(temp_dir)
            nested_directory = directory / "nested"
            nested_directory.mkdir()
            (directory / "z.pdf").write_text("root")
            (nested_directory / "a.pdf").write_text("nested")
            (nested_directory / ".hidden.pdf").write_text("hidden")

            files = FileService.list_files(directory)

            self.assertEqual(
                [path.relative_to(directory).as_posix() for path in files],
                ["nested/a.pdf", "z.pdf"],
            )


if __name__ == "__main__":
    unittest.main()
