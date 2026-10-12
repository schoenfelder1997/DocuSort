import sys

from PySide6.QtWidgets import QApplication

from docusort import __version__
from docusort.ui.main_window import MainWindow


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("DocuSort")
    app.setApplicationVersion(__version__)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
