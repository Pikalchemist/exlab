import random


class Ensemble(object):
    def __init__(self, list_or_dict):
        self.data = list_or_dict

    def __repr__(self):
        return self.data.__repr__()

    def __len__(self):
        return len(self.data)

    def sample(self):
        return random.choice(self.values())

    def values(self):
        if isinstance(self.data, list):
            return self.data
        return list(self.data.values())
