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


if __name__ == "__main__":
    unittest.main()
