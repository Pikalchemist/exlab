class Learner(object):
    def __init__(self, *args):
        # print(args)
        self.args = args
    
    def __repr__(self):
        return f'Learner{self.args}'
