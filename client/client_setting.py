class Setting:

    def __init__(self, endowment=20, multiplier=2):
        """

        Args:
            endowment: init units of the player
            multiplier: multiplier of the player
        """
        # minimum age for participating this experiment
        self.min_age = 18

        self.endowment = endowment
        self.multiplier = multiplier

        # UI file path
        self.experiment_filepath = "experiment.ui"

        # hostname: IP address of the server computer
        # port: port of the server computer
        self.hostname = "10.97.102.174"
        self.port = 1234
