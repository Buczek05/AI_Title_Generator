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
import shutil
from PyQt6.QtGui import QIcon

SETTINGS_PATH = os.path.expanduser("~") + "/.AI_Title_Generator/"
SETTINGS_FILE = SETTINGS_PATH + "settings.json"
GPT_SYSTEM_MESSAGE = "Create short (max 10 words) title for program based on it code, in tytle describe what this program do. Return only title."
GTP_SYSTEM_MESSAGE_DIR = {"role": "system", "content": GPT_SYSTEM_MESSAGE}


class Window(QDialog):
    def setup_window(self):
        self.main_layout = QVBoxLayout()
        self.setWindowTitle("Title Generator")
        self.resize(600, 100)
        self.setLayout(self.main_layout)

    def setup_layout_line(self, *widgets):
        line_layout = QHBoxLayout()
        for widget in widgets:
            line_layout.addWidget(widget)
        self.main_layout.addLayout(line_layout)

    def setup_layout(self):
        self.setup_api_line()
        self.setup_path()
        self.setup_output_folder()
        self.setup_generate_button()

    # API KEY
    def setup_view_api_line(self):
        self.api_key_label = QLabel("API key:")
        self.api_key_line_edit = QLineEdit()
        self.show_api_key_button = QToolButton()

    def setup_property_api_line(self):
        self.api_key_line_edit.textChanged.connect(self.changed_open_ai_api_key)
        self.show_api_key_button.setCheckable(True)
        self.show_api_key_button.toggled.connect(self.toggle_api_key_line_edit_show)

        self.hide_text_api_key_line_edit()

    def setup_api_line(self):
        self.setup_view_api_line()
        self.setup_property_api_line()
        self.setup_layout_line(
            self.api_key_label, self.api_key_line_edit, self.show_api_key_button
        )

    def show_text_api_key_line_edit(self):
        self.api_key_line_edit.setEchoMode(QLineEdit.EchoMode.Normal)
        self.show_api_key_button.setText("Hide")

    def hide_text_api_key_line_edit(self):
        self.api_key_line_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.show_api_key_button.setText("Show")

    def toggle_api_key_line_edit_show(self):
        if self.show_api_key_button.isChecked():
            self.show_text_api_key_line_edit()
        else:
            self.hide_text_api_key_line_edit()

    def changed_open_ai_api_key(self):
        try:
            openai.api_key = self.api_key_line_edit.text()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    # MAIN FILE PATH
    def setup_view_path(self):
        self.file_path_label = QLabel("Input file:")
        self.main_file_path = QLineEdit()
        self.choose_file_path_button = QToolButton()

    def setup_property_path(self):
        self.choose_file_path_button.setText("...")
        self.choose_file_path_button.clicked.connect(self.choose_file_path)

    def setup_path(self):
        self.setup_view_path()
        self.setup_property_path()
        self.setup_layout_line(
            self.file_path_label, self.main_file_path, self.choose_file_path_button
        )

    def choose_file_path(self):
        file_path = QFileDialog.getOpenFileName(self, "Choose input file")
        self.main_file_path.setText(file_path[0])

    # OUTPUT FOLDER
    def setup_view_output_folder(self):
        self.output_folder_label = QLabel("Output folder:")
        self.output_folder_edit = QLineEdit()
        self.choose_output_folder_button = QToolButton()

    def setup_property_output_folder(self):
        self.choose_output_folder_button.setText("...")
        self.choose_output_folder_button.clicked.connect(self.choose_output_folder)

    def setup_output_folder(self):
        self.setup_view_output_folder()
        self.setup_property_output_folder()
        self.setup_layout_line(
            self.output_folder_label,
            self.output_folder_edit,
            self.choose_output_folder_button,
        )

    def choose_output_folder(self):
        path = QFileDialog.getExistingDirectory(self, "Choose output folder")
        self.output_folder_edit.setText(path)

    # GENERATE BUTTON
    def setup_view_generate_button(self):
        self.generate_button = QPushButton("Generate")

    def setup_property_generate_button(self):
        self.generate_button.clicked.connect(self.generate)

    def setup_generate_button(self):
        self.setup_view_generate_button()
        self.setup_property_generate_button()
        self.main_layout.addWidget(self.generate_button)

    # SETTINGS
    def check_settings(self, settings_dict: dict) -> bool:
        if not settings_dict:
            return False

        for key in settings_dict:
            if not settings_dict[key]:
                return False

        return True

    def apply_settings(self, settings_dict: dict):
        self.api_key_line_edit.setText(settings_dict["api_key"])
        openai.api_key = settings_dict["api_key"]
        self.main_file_path.setText(settings_dict["input_file"])
        self.output_folder_edit.setText(settings_dict["output_folder"])

    def load_settings(self):
        settings_dict = self.load_user_settings()
        if self.check_settings(settings_dict):
            self.apply_settings(settings_dict)

    def __init__(self):
        super().__init__()

        self.setup_window()
        self.setup_layout()
        self.load_settings()

    def check_if_file_exist(self, path: str) -> bool:
        return os.path.exists(path)

    def check_if_file_is_text_file(self, path: str) -> bool:
        try:
            with open(path, "r") as f:
                f.read()
            return True
        except UnicodeDecodeError:
            return False

    def check_if_output_folder_exist(self, path: str) -> bool:
        return os.path.exists(path)

    def check_file_path(self, file_path) -> bool:
        if not self.check_if_file_exist(file_path):
            QMessageBox.critical(self, "Error", "File not found")
            return False
        if not self.check_if_file_is_text_file(file_path):
            QMessageBox.critical(self, "Error", "File is not text file")
            return False
        return True

    def check_output_folder(self, output_folder) -> bool:
        if not self.check_if_output_folder_exist(output_folder):
            QMessageBox.critical(self, "Error", "Output folder not found")
            return False
        return True

    def setup_file_path_and_output_folder_if_everything_is_ok(self) -> bool:
        self.file_path = self.main_file_path.text()
        self.output_folder = self.output_folder_edit.text()

        if not self.check_file_path(self.file_path) or not self.check_output_folder(
            self.output_folder
        ):
            return False
        return True

    def get_file_extension(self, file_path: str) -> str:
        return file_path.split(".")[-1]

    def get_file_content(self, file_path: str) -> str:
        with open(file_path, "r") as f:
            return f.read()

    def get_messages_to_ai(self, file_content: str) -> list:
        gpt_user_message = {"role": "user", "content": file_content}
        return [GTP_SYSTEM_MESSAGE_DIR, gpt_user_message]

    def get_response_from_ai(self, messages) -> dict:
        return openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
        )

    def generate_file_title(self) -> None:
        file_content = self.get_file_content(self.file_path)
        messages_to_ai = self.get_messages_to_ai(file_content)
        response_from_ai = self.get_response_from_ai(messages_to_ai)
        self.file_title_generated_by_ai = response_from_ai["choices"][0]["message"][
            "content"
        ]

    def get_output_file_path(self) -> str:
        file_extension = self.get_file_extension(self.file_path)
        output_file_path = (
            self.output_folder
            + "/"
            + self.file_title_generated_by_ai
            + "."
            + file_extension
        )
        return output_file_path

    def copy_file(self) -> bool:
        try:
            shutil.copyfile(self.file_path, self.output_file_path)
            return True
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            return False

    def generate(self):
        if not self.setup_file_path_and_output_folder_if_everything_is_ok():
            return
        self.generate_file_title()
        self.output_file_path = self.get_output_file_path()
        if not self.copy_file():
            return
        QMessageBox.information(
            self, "Success", "File saved as " + self.output_file_path
        )

    def create_dir_if_not_exists(self, path: str) -> None:
        if not os.path.exists(path):
            os.makedirs(path)

    def create_user_settings_dict(self) -> None:
        user_settings_dict = {
            "api_key": self.api_key_line_edit.text(),
            "input_file": self.main_file_path.text(),
            "output_folder": self.output_folder_edit.text(),
        }
        return user_settings_dict

    def save_user_settings_to_file(self, user_settings_dict: dict) -> None:
        json.dump(
            user_settings_dict,
            open(SETTINGS_FILE, "w"),
        )

    def save_user_settings(self) -> None:
        self.create_dir_if_not_exists(SETTINGS_PATH)
        user_settings_dict = self.create_user_settings_dict()
        self.save_user_settings_to_file(user_settings_dict)

    def load_user_settings(self) -> dict:
        try:
            user_settings_dict = json.load(open(SETTINGS_FILE, "r"))

        except FileNotFoundError:
            user_settings_dict = {}

        return user_settings_dict

    def closeEvent(self, event) -> None:
        self.save_user_settings()
        return super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    app.exec()
