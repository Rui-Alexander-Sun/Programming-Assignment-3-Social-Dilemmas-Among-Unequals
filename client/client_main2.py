from client_setting import Setting
from PyQt6.QtWidgets import QApplication
from experiment_window import ExperimentWindow


if __name__ == "__main__":
    # instantiate setting
    setting = Setting(20,1.5)

    app = QApplication([])
    window = ExperimentWindow(setting)

    window.show()
    app.exec()
