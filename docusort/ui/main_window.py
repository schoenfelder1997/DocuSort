from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QDir, QSettings, Qt
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QFileSystemModel,
    QFormLayout,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QTreeView,
    QVBoxLayout,
    QWidget,
)

from docusort.core.file_service import FileService
from docusort.core.metadata_extractor import MetadataExtractor


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("DocuSort")
        self.resize(1100, 700)

        self.settings = QSettings("DocuSort", "DocuSort")
        default_directory = Path.home() / "Documents"
        saved_source = Path(self.settings.value("source_directory", str(default_directory), type=str))
        saved_target = Path(self.settings.value("target_directory", str(default_directory), type=str))
        self.source_directory = saved_source if saved_source.is_dir() else default_directory
        self.target_directory = saved_target if saved_target.is_dir() else default_directory
        self.current_file: Path | None = None
        self.current_target_folder: Path | None = None

        self.file_service = FileService()
        self.metadata_extractor = MetadataExtractor()

        self._build_ui()
        self.load_target_directory()
        self.load_source_directory()

    def _build_ui(self) -> None:
        central = QWidget()
        main_layout = QHBoxLayout(central)

        left_column = QWidget()
        left_layout = QVBoxLayout(left_column)

        source_row = QHBoxLayout()
        self.source_button = QPushButton("Select Source Folder")
        self.source_button.clicked.connect(self.choose_source_directory)
        self.source_path_label = QLabel(self.source_directory.as_posix())
        source_row.addWidget(self.source_button)
        source_row.addWidget(self.source_path_label, 1)
        left_layout.addLayout(source_row)

        self.file_list = QListWidget()
        self.file_list.itemClicked.connect(self.on_file_selected)
        left_layout.addWidget(self.file_list)

        right_column = QWidget()
        right_layout = QVBoxLayout(right_column)

        target_row = QHBoxLayout()
        self.target_button = QPushButton("Select Target Folder")
        self.target_button.clicked.connect(self.choose_target_directory)
        self.target_path_label = QLabel(self.target_directory.as_posix())
        target_row.addWidget(self.target_button)
        target_row.addWidget(self.target_path_label, 1)
        right_layout.addLayout(target_row)

        self.create_folder_button = QPushButton("Create Folder in Target")
        self.create_folder_button.clicked.connect(self.create_target_folder)
        right_layout.addWidget(self.create_folder_button)

        self.target_tree = QTreeView()
        self.target_tree.setHeaderHidden(True)
        self.target_tree.setColumnWidth(0, 300)
        self.target_tree.setAlternatingRowColors(True)
        self.target_tree.clicked.connect(self.on_target_folder_selected)
        self.target_tree.expanded.connect(self.on_target_folder_selected)
        right_layout.addWidget(self.target_tree)

        metadata_widget = QWidget()
        form_layout = QFormLayout(metadata_widget)

        self.name_input = QLineEdit()
        self.topic_input = QLineEdit()
        self.date_input = QLineEdit()

        self.date_format_group = QWidget()
        date_layout = QHBoxLayout(self.date_format_group)
        self.date_radio_full = QRadioButton("YYYY-MM-dd")
        self.date_radio_month = QRadioButton("YYYY-MM")
        self.date_radio_year = QRadioButton("YYYY")
        self.date_radio_none = QRadioButton("No date")
        self.date_radio_full.setChecked(True)
        date_layout.addWidget(self.date_radio_full)
        date_layout.addWidget(self.date_radio_month)
        date_layout.addWidget(self.date_radio_year)
        date_layout.addWidget(self.date_radio_none)

        date_field = QWidget()
        date_field_layout = QVBoxLayout(date_field)
        date_field_layout.setContentsMargins(0, 0, 0, 0)
        date_field_layout.addWidget(self.date_input)
        date_field_layout.addWidget(self.date_format_group)

        form_layout.addRow("Date", date_field)
        form_layout.addRow("Topic", self.topic_input)
        form_layout.addRow("Name", self.name_input)
        for field in (self.date_input, self.topic_input, self.name_input):
            field.textChanged.connect(self.save_session_state)
        for radio in (self.date_radio_full, self.date_radio_month, self.date_radio_year, self.date_radio_none):
            radio.toggled.connect(self.save_session_state)

        self.process_button = QPushButton("Move & Rename File")
        self.process_button.clicked.connect(self.process_current_file)
        right_layout.addWidget(metadata_widget)
        right_layout.addWidget(self.process_button)

        main_layout.addWidget(left_column, 1)
        main_layout.addWidget(right_column, 2)
        self.setCentralWidget(central)

    def choose_source_directory(self) -> None:
        directory = QFileDialog.getExistingDirectory(self, "Select Source Folder", self.source_directory.as_posix())
        if directory:
            self.source_directory = Path(directory)
            self.source_path_label.setText(self.source_directory.as_posix())
            self.current_file = None
            self.settings.remove("current_file")
            self.load_source_directory()
            self.save_session_state()

    def choose_target_directory(self) -> None:
        directory = QFileDialog.getExistingDirectory(self, "Select Target Folder", self.target_directory.as_posix())
        if directory:
            self.target_directory = Path(directory)
            self.target_path_label.setText(self.target_directory.as_posix())
            self.current_target_folder = self.target_directory
            self.settings.setValue("selected_target_folder", str(self.target_directory))
            self.load_target_directory()
            self.save_session_state()

    def create_target_folder(self) -> None:
        if not self.target_directory.exists():
            QMessageBox.warning(self, "Target folder missing", "Please select a valid target folder first.")
            return

        folder_name, ok = QInputDialog.getText(self, "Create folder", "New folder name:")
        if not ok or not folder_name.strip():
            return

        new_folder = self.target_directory / folder_name.strip()
        new_folder.mkdir(parents=True, exist_ok=True)
        self.load_target_directory()

    def load_source_directory(self) -> None:
        self.file_list.clear()
        if not self.source_directory.exists():
            return
        for file_path in self.file_service.list_files(self.source_directory):
            item = QListWidgetItem(file_path.relative_to(self.source_directory).as_posix())
            item.setData(Qt.ItemDataRole.UserRole, str(file_path))
            self.file_list.addItem(item)

        saved_file = Path(self.settings.value("current_file", "", type=str))
        if saved_file.is_file():
            try:
                saved_file.relative_to(self.source_directory)
            except ValueError:
                return
            for index in range(self.file_list.count()):
                item = self.file_list.item(index)
                if Path(item.data(Qt.ItemDataRole.UserRole)) == saved_file:
                    self.file_list.setCurrentItem(item)
                    self.on_file_selected(item)
                    break

    def load_target_directory(self) -> None:
        if not self.target_directory.exists():
            self.target_directory.mkdir(parents=True, exist_ok=True)

        model = QFileSystemModel()
        model.setRootPath(self.target_directory.as_posix())
        model.setFilter(QDir.Dirs | QDir.NoDotAndDotDot)
        self.target_tree.setModel(model)
        for column in range(1, model.columnCount()):
            self.target_tree.hideColumn(column)

        root_index = model.index(self.target_directory.as_posix())
        self.target_tree.setRootIndex(root_index)
        saved_folder = Path(self.settings.value("selected_target_folder", str(self.target_directory), type=str))
        try:
            saved_folder.relative_to(self.target_directory)
            selected_folder = saved_folder if saved_folder.is_dir() else self.target_directory
        except ValueError:
            selected_folder = self.target_directory

        self.current_target_folder = selected_folder
        selected_index = model.index(selected_folder.as_posix())
        self.target_tree.setCurrentIndex(selected_index if selected_index.isValid() else root_index)
        self.target_path_label.setText(str(self.current_target_folder))
        ancestor_index = selected_index
        while ancestor_index.isValid():
            self.target_tree.expand(ancestor_index)
            if Path(model.filePath(ancestor_index)) == self.target_directory:
                break
            ancestor_index = ancestor_index.parent()
        self.target_tree.expandToDepth(1)
        self.target_tree.resizeColumnToContents(0)

    def on_target_folder_selected(self, index=None) -> None:
        model = self.target_tree.model()
        if model is None:
            return

        if index is None:
            index = self.target_tree.currentIndex()

        if not index.isValid():
            self.current_target_folder = self.target_directory
            return

        path = Path(model.filePath(index))
        if path.is_dir():
            self.current_target_folder = path
            self.target_path_label.setText(path.as_posix())
        else:
            parent = path.parent
            self.current_target_folder = parent
            self.target_path_label.setText(parent.as_posix())
        self.save_session_state()

    def on_file_selected(self, item: QListWidgetItem) -> None:
        if not self.source_directory.exists():
            return

        self.current_file = Path(item.data(Qt.ItemDataRole.UserRole))
        metadata = self.metadata_extractor.extract(self.current_file)

        saved_file = self.settings.value("current_file", "", type=str)
        resume_values = {}
        if saved_file == str(self.current_file):
            resume_values = {
                "name": self.settings.value("pending_name", metadata["title"], type=str),
                "topic": self.settings.value("pending_topic", "General", type=str),
                "date": self.settings.value("pending_date", metadata["date"], type=str),
                "date_format": self.settings.value("pending_date_format", "YYYY-MM-dd", type=str),
            }

        topic = metadata.get("category", "").strip()
        company = metadata.get("company", "").strip()
        if not topic or topic.lower() in {"general", "unknown"}:
            topic = company if company.lower() != "unknown" else "General"

        self.name_input.setText(resume_values.get("name", metadata["title"]))
        self.topic_input.setText(resume_values.get("topic", topic))
        self.date_input.setText(resume_values.get("date", metadata["date"]))
        date_radios = {
            "YYYY-MM-dd": self.date_radio_full,
            "YYYY-MM": self.date_radio_month,
            "YYYY": self.date_radio_year,
            "None": self.date_radio_none,
        }
        date_radios.get(resume_values.get("date_format"), self.date_radio_full).setChecked(True)

        self.current_target_folder = self.target_directory
        if self.target_tree.model():
            index = self.target_tree.currentIndex()
            if index.isValid():
                path = self.target_tree.model().filePath(index)
                if Path(path).is_dir():
                    self.current_target_folder = Path(path)
        self.save_session_state()

    def save_session_state(self) -> None:
        self.settings.setValue("source_directory", str(self.source_directory))
        self.settings.setValue("target_directory", str(self.target_directory))
        if self.current_target_folder is not None:
            self.settings.setValue("selected_target_folder", str(self.current_target_folder))

        if self.current_file is None or not self.current_file.is_file():
            return

        self.settings.setValue("current_file", str(self.current_file))
        self.settings.setValue("pending_name", self.name_input.text())
        self.settings.setValue("pending_topic", self.topic_input.text())
        self.settings.setValue("pending_date", self.date_input.text())
        if self.date_radio_month.isChecked():
            date_format = "YYYY-MM"
        elif self.date_radio_year.isChecked():
            date_format = "YYYY"
        elif self.date_radio_none.isChecked():
            date_format = "None"
        else:
            date_format = "YYYY-MM-dd"
        self.settings.setValue("pending_date_format", date_format)

    def process_current_file(self) -> None:
        if self.current_file is None:
            QMessageBox.warning(self, "No file selected", "Please select a file to process.")
            return

        name = self.name_input.text()
        date_value = self.date_input.text()
        topic = self.topic_input.text()

        if not self.current_target_folder or not self.current_target_folder.exists():
            self.current_target_folder = self.target_directory

        date_format = "YYYY-MM-dd"
        if self.date_radio_full.isChecked():
            date_format = "YYYY-MM-dd"
        elif self.date_radio_month.isChecked():
            date_format = "YYYY-MM"
        elif self.date_radio_year.isChecked():
            date_format = "YYYY"
        else:
            date_format = "None"

        target_name = self.file_service.generate_target_name(date_value, topic, name, self.current_file.suffix, date_format)
        final_path = self.file_service.ensure_unique_destination(self.current_target_folder, target_name)

        if final_path.exists():
            choice = QMessageBox.question(
                self,
                "File already exists",
                "A file with this name already exists. Do you want to keep the generated name with a suffix?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if choice == QMessageBox.StandardButton.Yes:
                final_path = self.file_service.ensure_unique_destination(self.current_target_folder, target_name)
            else:
                custom_name, ok = QInputDialog.getText(self, "Rename file", "Choose a custom file name:")
                if not ok or not custom_name.strip():
                    return
                final_path = self.current_target_folder / f"{custom_name.strip()}{self.current_file.suffix}"

        final_destination = self.file_service.move_to_destination(self.current_file, final_path)
        QMessageBox.information(self, "File moved", f"File moved to:\n{final_destination}")
        self.load_source_directory()
        self.load_target_directory()
        self.current_file = None
        self.settings.remove("current_file")
        self.save_session_state()

    def closeEvent(self, event) -> None:
        self.save_session_state()
        self.settings.sync()
        super().closeEvent(event)


def main() -> None:
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
