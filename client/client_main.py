from client_setting import Setting
from PyQt6.QtWidgets import QApplication
from experiment_window import ExperimentWindow
from threading import Thread
from client import communicate

if __name__ == "__main__":
    # instantiate setting
    setting = Setting(20,2)

    app = QApplication([])
    window = ExperimentWindow(setting)

    # create a thread for communication between server computer and client
    # while running the experiment
    communication = Thread(target=communicate, args=(setting,window,))
    communication.start()

    window.show()
    app.exec()
