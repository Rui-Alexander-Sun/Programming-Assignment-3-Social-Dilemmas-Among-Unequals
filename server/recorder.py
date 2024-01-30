import os
import pandas as pd


class Recorder:

    def __init__(self, setting):
        '''

        Args:
            setting: server settings
        '''
        self.trial_data = []
        self.data_path = setting.output_data_path

        self.session = 0
        self.trial = 1
        self.player_number = setting.players_num
        self.df = self.init_csv()
        self.ppt_names = []
        self.ppt_demographics = []

    def init_header(self):
        header = ["Session", "Trial", 'Total players', "Player name", "Income",
                  "Multiplier", "Contribution", "Multiplied Contribution",
                  'Remains', 'Group contribution',
                  'Group multiplied contribution', 'Share per person', 'Payoff',
                  'Age', 'Gender', 'Education', 'Race']
        return header

    def init_csv(self):
        """initialize the csv file
        create a new csv file if no such file
        """
        if os.path.exists(self.data_path):
            df = pd.read_csv(self.data_path)
            last_session = df.iloc[-1, 0]
            self.session = last_session + 1
        else:
            header = self.init_header()
            df = pd.DataFrame(columns=header)
            self.session = 1
        return df

    def calculate_group_contribution(self, contri_info):
        group_contribution = 0
        for info in contri_info:
            contribution = info[2]
            group_contribution += contribution
        return group_contribution

    def append_trial_data(self, contri_info, results):
        group_multiplied_contribution, share_per_person = results
        group_contribution = self.calculate_group_contribution(contri_info)
        for i, player_info in enumerate(contri_info):
            player_name = self.ppt_names[i]
            player_demo = self.ppt_demographics[i]
            income, multiplier, contribution, multiplied_contribution, remains = player_info
            payoff = share_per_person + remains
            row = [self.session, self.trial, self.player_number, player_name,
                   income, multiplier, contribution, multiplied_contribution,
                   remains, group_contribution, group_multiplied_contribution,
                   share_per_person, payoff]
            row.extend(player_demo)
            row_df = pd.DataFrame([row], columns=self.df.columns)
            self.df = pd.concat([self.df, row_df],
                                ignore_index=True, axis = 0)

    def data2csv(self):
        """dataframe to csv"""
        self.df.to_csv(self.data_path, index=False)
