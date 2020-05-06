from exlab.modular.logger import Logger


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
        self.logger = None

        # Hierarchy
        self.children = set()

        if isinstance(parent, Modular):
            parent = parent.module
        self.parent = None
        self.attach(parent)
        
        self.time = 0

        # Logging
        self.logger = Logger(self)
        self.logger.info('Module \'{}\' has been started'.format(self.name))
    
    def add_child(self, module):
        if module is None:
            return
        if module.parent:
            module.detached()
            module.parent.children.remove(module)
        self.children.add(module)
        module.parent = self
        module.attached()

    def attach(self, parent):
        if parent is None:
            return
        if self.parent:
            self.detached()
            self.parent.children.remove(self)
        parent.children.add(self)
        self.parent = parent
        self.attached()
    
    def attached(self):
        if self.logger:
            self.logger.update()
            self.logger.info('Module \'{}\' has been attached to \'{}\''.format(self.name, self.parent.name))
    
    def detached(self):
        if self.logger:
            self.logger.update()
    
    @property
    def root(self):
        root = self
        while root.parent:
            root = root.parent
        return root
    
    def all_children(self):
        children = set()
        for child in self.children:
            children.add(child)
            children |= child.all_children
        return children


if __name__ == '__main__':
    class Test(Modular):
        def __init__(self):
            Modular.__init__(self, 'Test')

    t = Test()
    with t.logger.error('Hello :)', tag='test'):
        t.logger.error('Hello :)', tag='test')

