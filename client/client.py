import pickle
import socket


class Client:

    def __init__(self, setting, window):
        '''

        Args:
            setting: client_setting
            window: experiment window
        '''

        # server of this experiment
        self.server = socket.socket()
        self.hostname = setting.hostname
        self.port = setting.port
        self.window = window

        # name of the player
        # age of the player
        # gender of the player
        # education level of the player
        # race of the player
        self.name = ''
        self.ppt_age = window.ppt_age
        self.ppt_gender = window.ppt_gender
        self.ppt_edu = window.ppt_edu
        self.ppt_race = window.ppt_race

        # connect to the server
        self.server.connect((self.hostname, self.port))
        # send demographic information to the server
        self.init_info()
        self.running()

    def init_info(self):
        demographics = [self.ppt_age,
                        self.ppt_gender,
                        self.ppt_edu,
                        self.ppt_race]
        msg = ("demo", demographics)
        self.send_msg(msg)

        server_msg = self.server.recv(1024)
        command, msg = pickle.loads(server_msg)
        if command == 'init':
            players_num, player_name = msg
            self.name = player_name
            self.window.init_result_table(players_num, player_name)
        self.window.all_finished = True

    def send_contribution(self, result):
        '''
        send contribution msg to the server

        Args:
            result: result of the player in this trial

        Returns: None

        '''
        msg = ('contri', result)
        self.send_msg(msg)

    def send_msg(self, msg):
        '''
        send msg to the server

        Args:
            msg: message to be sent

        Returns:

        '''
        msg = pickle.dumps(msg)
        self.server.send(msg)

    def close(self):
        self.server.close()



    def running(self):
        while True:
            # if the player has filled in demographic information,
            # receive message from the server and initialize the result table
            # if the player has contributed,
            # send their result and wait for other players
            if self.window.contributed:
                income = self.window.income
                contri = self.window.contribution
                multiplier = self.window.multiplier
                multiplied_contri = self.window.multiplied_contri
                remains = self.window.remains
                result = [income, multiplier, contri, multiplied_contri,
                          remains]
                self.send_contribution(result)

                # receive message from the server
                server_msg = self.server.recv(1024)
                command, msg = pickle.loads(server_msg)
                # if it is the last trial
                if command == 'end':
                    self.window.pButton_continue.clicked.disconnect(self.window.new_trial)
                    self.window.pButton_continue.clicked.connect(
                        self.window.switch_to_next_page)
                # set the result table and payoff table
                self.window.display_result_and_payoff(msg)
                self.window.contributed = False
                self.window.all_finished = True


def create_client(setting, window):
    client = Client(setting, window)