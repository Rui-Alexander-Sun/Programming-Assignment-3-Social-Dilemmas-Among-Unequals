import socket
import pickle


def calculate(contri_info):
    ''' calculate group contribution and share per person

    Args:
        contri_info: contribution information

    Returns: results

    '''
    total = 0
    for player_info in contri_info:
        multiplied_contri = player_info[3]
        total += multiplied_contri
    share_per_person = round(total / len(contri_info), 2)
    results = [total, share_per_person]
    return results


class Server:

    def __init__(self, setting, recorder):
        self.setting = setting
        self.recorder = recorder

        self.hostname = socket.gethostname()
        self.server = self.set_server()

        self.clients = []
        self.connected_clients_num = 0

        self.contri_info = []
        self.trial_num = 0

        self.connecting()
        self.init_info()
        self.running()

    def set_server(self):
        '''set server attributes'''
        server = socket.socket()
        server.bind((self.hostname, self.setting.port))
        server.listen(self.setting.players_num)
        return server

    def send_msg(self, msg):
        msg = pickle.dumps(msg)
        for client in self.clients:
            client.send(msg)

    def init_info(self):
        command = 'init'
        i = 1
        for client in self.clients:
            name = 'Player ' + str(i)
            self.recorder.ppt_names.append(name)
            list = [self.setting.players_num, name]
            msg = [command, list]
            msg = pickle.dumps(msg)
            client.send(msg)
            i += 1

    def connecting(self):
        '''accept new clients'''
        while self.connected_clients_num < self.setting.players_num:
            client, address = self.server.accept()
            self.clients.append(client)
            self.connected_clients_num += 1

    def update(self):
        self.trial_num += 1
        self.recorder.trial = self.trial_num
        results = calculate(self.contri_info)
        self.recorder.append_trial_data(self.contri_info, results)
        self.contri_info.append(results)

    def check_if_end(self):
        if self.trial_num == self.setting.max_trials_num:
            self.recorder.data2csv()
            command = 'end'
        else:
            command = 'contri'
        msg = [command, self.contri_info]
        return msg

    def running(self):
        while True:
            # receive messages from the clients
            for client in self.clients:
                client_msg = client.recv(1024)
                command, msg = pickle.loads(client_msg)
                # if receive demographic information, record
                if command == "demo":
                    self.recorder.ppt_demographics.append(msg)
                # if receive contribution information, calculate and record
                elif command == 'contri':
                    self.contri_info.append(msg)
                    if len(self.contri_info) == self.setting.players_num:
                        self.update()
                        msg = self.check_if_end()
                        self.send_msg(msg)
                        self.contri_info = []
