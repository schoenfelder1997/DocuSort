import sys

from PySide6.QtWidgets import QApplication

from docusort.ui.main_window import MainWindow


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("DocuSort")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
