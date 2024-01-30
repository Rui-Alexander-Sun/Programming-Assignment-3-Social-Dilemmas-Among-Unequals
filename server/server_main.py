from server_setting import Setting
from server import Server
from recorder import Recorder


if __name__ == '__main__':
    setting = Setting()
    recorder = Recorder(setting)
    server = Server(setting, recorder)