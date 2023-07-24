import main
from main import *
from PyQt6.QtCore import Qt

main.SETTINGS_FILE = "test_settings.json"


class TestClass:
    API = "test_api_key"
    INPUT_FILE = "test_input_file.py"
    OUTPUT_FOLDER = "."

    def test_settings(self):
        save_settings(self.API, self.INPUT_FILE, self.OUTPUT_FOLDER)
        settings = get_settings()
        assert settings["api_key"] == self.API
        assert settings["input_file"] == self.INPUT_FILE
        assert settings["output_folder"] == self.OUTPUT_FOLDER
        os.remove(main.SETTINGS_FILE)

    def test_window_init(self, qtbot):
        save_settings(self.API, self.INPUT_FILE, self.OUTPUT_FOLDER)
        window = Window()
        qtbot.addWidget(window)
        assert window.api_key_edit.text() == self.API
        assert window.path_edit.text() == self.INPUT_FILE
        assert window.output_folder_edit.text() == self.OUTPUT_FOLDER
        os.remove(main.SETTINGS_FILE)

    # def test_setup_api_key(self, qtbot):
    #     save_settings(self.API, self.INPUT_FILE, self.OUTPUT_FOLDER)
    #     window = Window()
    #     qtbot.addWidget(window)
    #     window.api_key_edit.setText("new_api_key")
    #     window.setup_api_key()
    #     assert window.api_key_edit.text() == "new_api_key"
    #     os.remove(SETTINGS_FILE)

    def test_show_hide_api_key(self, qtbot):
        save_settings(self.API, self.INPUT_FILE, self.OUTPUT_FOLDER)
        window = Window()
        qtbot.addWidget(window)
        window.show_api_key_button.click()
        assert window.api_key_edit.echoMode() == QLineEdit.EchoMode.Normal
        window.show_api_key_button.click()
        assert window.api_key_edit.echoMode() == QLineEdit.EchoMode.Password
        os.remove(main.SETTINGS_FILE)

    def test_generate(self, qtbot):
        try:
            settings = json.load(open(SETTINGS_PATH + "settings.json", "r"))
        except:
            raise Exception("Setup api key in app, and then run this test")
        api = settings["api_key"]
        save_settings(api, self.INPUT_FILE, self.OUTPUT_FOLDER)

        test_file_code = "print('Hello, World!')"
        with open(self.INPUT_FILE, "w") as f:
            f.write(test_file_code)

        window = Window()
        qtbot.addWidget(window)
        window.generate()
        assert os.path.exists(self.OUTPUT_FOLDER)
        assert window.file_title
        assert os.path.exists(window.output_file_path)

        os.remove(self.INPUT_FILE)
        os.remove(window.output_file_path)
        os.remove(main.SETTINGS_FILE)

    def test_close_event(self, qtbot):
        window = Window()
        qtbot.addWidget(window)
        window.api_key_edit.setText(self.API)
        window.path_edit.setText(self.INPUT_FILE)
        window.output_folder_edit.setText(self.OUTPUT_FOLDER)
        window.closeEvent(QtGui.QCloseEvent())
        setting = get_settings()
        assert setting["api_key"] == self.API
        assert setting["input_file"] == self.INPUT_FILE
        assert setting["output_folder"] == self.OUTPUT_FOLDER
        assert os.path.exists(main.SETTINGS_FILE)
        os.remove(main.SETTINGS_FILE)
