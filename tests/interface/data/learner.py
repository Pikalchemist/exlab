from exlab.interface.serializer import Serializable


class Learner(object):
    def __init__(self, *args):
        self.args = args
    
    def __repr__(self):
        return f'Learner{self.args}'


class SerialLearner(Serializable):
    def __init__(self, *args):
        self.args = args

    def __repr__(self):
        return f'Learner{self.args}'

    @classmethod
    def _deserialize(cls, dict_, serializer, obj=None):
        obj = cls(dict_.get('name'), dict_.get('obj'))

        serializer.set('learner',  obj)

        return obj


class Mod(object):
    def __init__(self, *args):
        self.args = args

    def __repr__(self):
        return f'Mod{self.args}'
