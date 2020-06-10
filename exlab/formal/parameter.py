

class HyperParameter(object):
    def __init__(self, value=None, name=None, help=None, range=None, how_to_choose=None):
        self.value = value
        self.name = name
        self.help = help
        self.range = range
        self.how_to_choose = how_to_choose


