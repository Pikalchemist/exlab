from .logger import Logger


class Modular(object):
    def __init__(self, name='', parent=None):
        self.module = Module(self, name, parent)
    
    @property
    def logger(self):
        return self.module.logger


class Module(object):
    def __init__(self, modular, name:str = '', parent=None):
        self.modular = modular
        self.name = name if name else self.modular.__class__.__name__

        # Hierarchy
        self.children = set()

        if isinstance(parent, Modular):
            parent = parent.modular
        self.parent = parent
        if self.parent:
            self.parent.children.add(self)

        # Logging
        self._logger = Logger(self)

        self.time = 0
    
    def root(self):
        root = self
        while root.parent:
            root = root.parent
        return root
    
    @property
    def logger(self):
        return self._logger


if __name__ == '__main__':
    class Test(Modular):
        def __init__(self):
            Modular.__init__(self, 'Test')

    t = Test()
    t.logger.error('Hello :)', tag='test')
    t.logger.error('Hello :)', tag='test')

