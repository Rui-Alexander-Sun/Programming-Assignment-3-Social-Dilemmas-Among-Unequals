from PyQt6.QtWidgets import QMainWindow, QTableWidgetItem
from PyQt6.uic import loadUi
from client import create_client
from threading import Thread


class ExperimentWindow(QMainWindow):
    """class of experiment window, inherited from QMainWindow"""

    def __init__(self, setting):
        """

        Args:
            setting: client settings for this experiment
        """
        super().__init__()

        self.setting = setting

        self.ppt_age = 0
        self.ppt_gender = ''
        self.ppt_edu = ''
        self.ppt_race = ''

        # Below Boolean variables are about whether the subject(s) have finished
        # a certain process
        # self.finished: whether this subject has finished a process
        # self.all_finished: whether all subjects have finished a process
        # self.contributed: whether this subject has contributed
        self.finished = False
        self.all_finished = False
        self.contributed = False

        self.players_num = 0
        self.income = self.setting.endowment
        self.multiplier = self.setting.multiplier
        self.contribution = 0
        self.multiplied_contri = 0
        self.remains = 0
        self.payoff = 0

        # load UI file
        loadUi(self.setting.experiment_filepath, self)

        # Connect push button with switching to next page
        self.pButton_consent.clicked.connect(self.consent_check)
        self.pButton_demography.clicked.connect(self.demography_check)
        self.pButton_comprehension.clicked.connect(self.comprehension_check)
        self.pButton_submit.clicked.connect(self.contribution_check)
        self.pButton_continue.clicked.connect(self.new_trial)

        # initialize the income text widgets
        self.set_income_text()

    # The following functions are organized logically(alphabetically)

    def init_result_table(self, players_num, player_name):
        """

        Args:
            players_num: number of players in this game
            player_name: player name of the current subject

        Returns: None

        """
        # set the number of rows in the result_table to
        # the number of players plus two
        self.players_num = players_num
        self.result_table.setRowCount(players_num + 2)
        # add player names to the table, see the comments below
        for i in range(1, players_num+1):
            name = 'Player ' + str(i)
            item = QTableWidgetItem(name)
            self.result_table.setItem(i-1, 1, item)
        # indicate which player the subject is in the result_table
        # E.g., if the subject is Player 2, the table will look like:
        #          Player      Income   ...
        #          Player 1
        # You >>>  Player 2
        #          ...
        # This design completely replicated the original study
        indicator = "You >>>"
        player_seq = int(player_name[-1])
        item = QTableWidgetItem(indicator)
        self.result_table.setItem(player_seq - 1, 0, item)

    def consent_check(self):
        """switch to demographic widget"""
        if self.checkBox.isChecked():
            self.switch_to_next_page()
        else:
            self.warning_unchecked.setText('Please tick the check box.')

    def warn_message(self, widget_name):
        """show warning message for blank information"""
        self.warning_blank.setText(f'Please fill in {widget_name} information.')

    def age_not_satisfied(self):
        """show warning message if participants' age do not meet the
        requirements of this experiment"""
        self.warning_blank.setText(
            "Sorry, you are not eligible for this experiment"
            " for the reason of age.")

    def demography_check(self):
        """switch to trial widgets"""
        age_value = self.age.value()

        # participants under min_age are not allowed to continue
        if age_value < self.setting.min_age:
            self.age_not_satisfied()
        # show warning message
        else:
            if self.gender.currentText() == "":
                self.warn_message(self.gender.objectName())
            elif self.education.currentText() == "":
                self.warn_message(self.education.objectName())
            elif self.race.currentText() == "":
                self.warn_message(self.race.objectName())
            else:
                self.ppt_age = self.age.value()
                self.ppt_gender = self.gender.currentText()
                self.ppt_edu = self.education.currentText()
                self.ppt_race = self.race.currentText()
                self.switch_to_next_page()

    def comprehension_check(self):
        # create a thread for communication between server computer and client
        # while running the experiment
        client_running = Thread(target=create_client,
                                args=(self.setting, self,))
        client_running.start()
        waiting = True
        # after finished the instructions, wait for other players
        while waiting:
            if self.all_finished:
                self.switch_to_next_page()
                self.all_finished = False
                self.contri_input.setMaximum(self.income)
                waiting = False

    def calculate(self):
        '''calculate multiplied contribution and remains'''
        self.multiplied_contri = self.contribution * self.multiplier
        self.remains = self.income - self.contribution

    def contribution_check(self):
        self.contribution = self.contri_input.value()
        self.calculate()
        self.contributed = True
        waiting = True
        # after contributed to the common pool, wait for other players
        while waiting:
            if self.all_finished:
                self.switch_to_next_page()
                self.all_finished = False
                waiting = False

    def new_trial(self):
        """a new trial"""
        # clear the text before
        # switch to the page before
        self.update_income()
        self.contri_input.setValue(0)
        self.contri_input.setMaximum(int(self.income))
        self.set_income_text()
        self.switch_to_last_page()

    def set_income_text(self):
        income_text = f'Your income is {self.income} units.'
        hint_text = f'(Type a value between 0 and {int(self.income)}.)'
        self.contri_income.setText(income_text)
        self.contri_hint.setText(hint_text)

    def update_income(self):
        self.income = self.payoff

    def display_result_and_payoff(self, msg):
        ''' display result table and payoff table

        Args:
            msg: message from the server

        Returns:

        '''
        total, share_per_person = msg[-1]
        total_text = f'Total: {str(total)}'
        item = QTableWidgetItem(total_text)
        self.result_table.setItem(self.players_num, 5, item)

        share_per_person_text = f'Share per person: {str(share_per_person)}'
        item = QTableWidgetItem(share_per_person_text)
        self.result_table.setItem(self.players_num+1, 5, item)

        item = QTableWidgetItem(str(share_per_person))
        self.payoff_table.setItem(1, 0, item)

        item = QTableWidgetItem(str(self.remains))
        self.payoff_table.setItem(0, 0, item)

        self.payoff = self.remains + share_per_person
        item = QTableWidgetItem(str(self.payoff))
        self.payoff_table.setItem(2, 0, item)

        for row, player_info in enumerate(msg[:-1]):
            for col, info in enumerate(player_info[:-1]):
                item = QTableWidgetItem(str(info))
                self.result_table.setItem(row, col+2, item)

    def switch_to_next_page(self):
        """switch to the next page"""
        current_index = self.stackedWidget.currentIndex()
        next_index = (current_index + 1) % self.stackedWidget.count()
        self.stackedWidget.setCurrentIndex(next_index)

    def switch_to_last_page(self):
        '''switch to the page before'''
        current_index = self.stackedWidget.currentIndex()
        next_index = (current_index - 1) % self.stackedWidget.count()
        self.stackedWidget.setCurrentIndex(next_index)