

class Experiment(object):
    def __init__(self, lab, database=None):
        self.lab = lab
        self.config = {}
        self.database = database
