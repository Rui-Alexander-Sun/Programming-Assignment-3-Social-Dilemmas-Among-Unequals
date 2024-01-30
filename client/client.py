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
        self.send_demographics()

    def send_demographics(self):
        ''' send demographic information to the server '''
        demographics = [self.ppt_age,
                        self.ppt_gender,
                        self.ppt_edu,
                        self.ppt_race]
        msg = ("demo", demographics)
        self.send_msg(msg)

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


def communicate(setting, window):
    no_client = True
    # if there is not a client, create one after finishing the demographic page
    while no_client:
        if window.finished and no_client:
            client = Client(setting, window)
            no_client = False
    while not no_client:
        # if the player has filled in demographic information,
        # receive message from the server and initialize the result table
        if window.finished:
            server_msg = client.server.recv(1024)
            command, msg = pickle.loads(server_msg)
            if command == 'init':
                players_num, player_name = msg
                client.name = player_name
                window.init_result_table(players_num, player_name)
            window.all_finished = True
            window.finished = False
        # if the player has contributed,
        # send their result and wait for other players
        elif window.contributed:
            income = window.income
            contri = window.contribution
            multiplier = window.multiplier
            multiplied_contri = window.multiplied_contri
            remains = window.remains
            result = [income, multiplier, contri, multiplied_contri, remains]
            client.send_contribution(result)

            # receive message from the server
            server_msg = client.server.recv(1024)
            command, msg = pickle.loads(server_msg)
            # if it is the last trial
            if command == 'end':
                window.pButton_continue.clicked.disconnect(window.new_trial)
                window.pButton_continue.clicked.connect(
                    window.switch_to_next_page)
            # set the result table and payoff table
            window.display_result_and_payoff(msg)
            window.contributed = False
            window.all_finished = True
            window.finished = False
