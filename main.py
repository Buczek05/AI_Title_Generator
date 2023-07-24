from PyQt6 import QtGui
import openai, json, os, sys
from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QFileDialog,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QLineEdit,
    QToolButton,
    QHBoxLayout,
    QLabel,
)
from PyQt6.QtGui import QIcon

SETTINGS_PATH = os.path.expanduser("~") + "/Documents/AI_Title_Generator/"
SETTINGS_FILE = SETTINGS_PATH + "settings.json"


def save_settings(api_key: str, input_file: str, output_folder: str) -> None:
    """Save settings to json file"""
    if not os.path.exists(SETTINGS_PATH):
        os.makedirs(SETTINGS_PATH)
    json.dump(
        {"api_key": api_key, "input_file": input_file, "output_folder": output_folder},
        open(SETTINGS_FILE, "w"),
    )
    print(SETTINGS_FILE)


def get_settings() -> dict:
    """Get settings from json file"""
    try:
        return json.load(open(SETTINGS_FILE, "r"))
    except FileNotFoundError:
        return {}


class Window(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Title Generator")
        self.resize(600, 100)

        self.api_key_label = QLabel("API key:")
        self.api_key_edit = QLineEdit()
        self.api_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.show_api_key_button = QToolButton()
        self.show_api_key_button.setText("Show")
        self.show_api_key_button.setCheckable(True)
        self.show_api_key_button.toggled.connect(self.show_hide_api_key)
        self.lyt_api_key = QHBoxLayout()
        self.lyt_api_key.addWidget(self.api_key_label)
        self.lyt_api_key.addWidget(self.api_key_edit)
        self.lyt_api_key.addWidget(self.show_api_key_button)
        self.api_key_edit.textChanged.connect(self.setup_api_key)

        self.path_label = QLabel("Input file:")
        self.path_edit = QLineEdit()
        self.choose_path_button = QToolButton()
        self.choose_path_button.setText("...")
        self.choose_path_button.clicked.connect(self.choose_path)
        self.lyt_path = QHBoxLayout()
        self.lyt_path.addWidget(self.path_label)
        self.lyt_path.addWidget(self.path_edit)
        self.lyt_path.addWidget(self.choose_path_button)

        self.output_folder_label = QLabel("Output folder:")
        self.output_folder_edit = QLineEdit()
        self.choose_output_folder_button = QToolButton()
        self.choose_output_folder_button.setText("...")
        self.choose_output_folder_button.clicked.connect(self.choose_output_folder)
        self.lyt_output_folder = QHBoxLayout()
        self.lyt_output_folder.addWidget(self.output_folder_label)
        self.lyt_output_folder.addWidget(self.output_folder_edit)
        self.lyt_output_folder.addWidget(self.choose_output_folder_button)

        self.generate_button = QPushButton("Generate")
        self.generate_button.clicked.connect(self.generate)

        self.lyt = QVBoxLayout()
        self.lyt.addLayout(self.lyt_api_key)
        self.lyt.addLayout(self.lyt_path)
        self.lyt.addLayout(self.lyt_output_folder)
        self.lyt.addWidget(self.generate_button)
        self.setLayout(self.lyt)

        settings = get_settings()
        try:
            if settings:
                self.api_key_edit.setText(settings["api_key"])
                openai.api_key = settings["api_key"]
                self.path_edit.setText(settings["input_file"])
                self.output_folder_edit.setText(settings["output_folder"])
        except KeyError:
            pass

    def setup_api_key(self):
        """Setup api key for openai"""
        try:
            openai.api_key = self.api_key_edit.text()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def show_hide_api_key(self):
        """Switch between showing and hiding api key by changing echo mode of QLineEdit"""
        if self.show_api_key_button.isChecked():
            self.api_key_edit.setEchoMode(QLineEdit.EchoMode.Normal)
            self.show_api_key_button.setText("Hide")
        else:
            self.api_key_edit.setEchoMode(QLineEdit.EchoMode.Password)

    def choose_path(self):
        """Choose input file by opening file dialog"""
        path = QFileDialog.getOpenFileName(self, "Choose input file")
        self.path_edit.setText(path[0])

    def choose_output_folder(self):
        """Choose output folder by opening file dialog"""
        path = QFileDialog.getExistingDirectory(self, "Choose output folder")
        self.output_folder_edit.setText(path)

    def generate(self):
        """Use GPT-3 to generate title for program based on it code"""
        try:
            with open(self.path_edit.text(), "r") as f:
                text = f.read()
        except FileNotFoundError:
            QMessageBox.critical(self, "Error", "File not found")
            return
        except UnicodeDecodeError:
            QMessageBox.critical(self, "Error", "File is not a text file")
            return

        message_to_GPT = "Create short (max 10 words) title for program based on it code, in tytle describe what this program do. Return only title."

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": message_to_GPT},
                {"role": "user", "content": text},
            ],
        )
        self.file_title = response["choices"][0]["message"]["content"]
        input_file_extension = self.path_edit.text().split(".")[-1]
        self.output_file_path = (
            self.output_folder_edit.text()
            + "/"
            + self.file_title
            + "."
            + input_file_extension
        )
        with open(self.output_file_path, "w") as f:
            f.write(text)
        QMessageBox.information(
            self, "Success", "File saved as " + self.output_file_path
        )

    def closeEvent(self, event) -> None:
        """Save settings on close"""
        save_settings(
            self.api_key_edit.text(),
            self.path_edit.text(),
            self.output_folder_edit.text(),
        )
        return super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    app.exec()
