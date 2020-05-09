from exlab.modular.logger import Logger


class Modular(object):
    def __init__(self, name='', parent=None):
        self.module = Module(self, name, parent)
    
    @property
    def logger(self):
        return self.module.logger


class Node(object):
    def __init__(self, host, parent=None):
        self.host = host

        # Hierarchy
        self.children = set()

        if isinstance(parent, Modular):
            parent = parent.module
        self.parent = None
        self.attach(parent)

    def add_child(self, node):
        if node is None:
            return
        if node.parent:
            node.detached()
            node.parent.children.remove(node)
        self.children.add(node)
        node.parent = self
        node.attached()

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
        pass

    def detached(self):
        pass

    def attach_counter(self, counter):
        self._counter = counter

    @property
    def root(self):
        root = self
        while root.parent:
            root = root.parent
        return root

    @property
    def counter(self):
        node = self
        while node.parent and not node._counter:
            node = node.parent
        return node._counter

    def all_children(self):
        children = set()
        for child in self.children:
            children.add(child)
            children |= child.all_children
        return children


class Module(Node):
    def __init__(self, host, name:str = '', parent=None):
        self.logger = None
        super().__init__(host, parent)

        self.name = name if name else self.host.__class__.__name__
        
        self._counter = None

        # Logging
        self.logger = Logger(self)
        self.logger.info('Module \'{}\' has been started'.format(self.name))
    
    @property
    def time(self):
        counter = self.counter
        if not counter:
            return -1
        return counter.t
    
    @property
    def children_modules(self):
        return set(child for child in self.children if isinstance(child, Module))
    
    def attached(self):
        super()
        if self.logger:
            self.logger.update()
            self.logger.info('Module \'{}\' has been attached to \'{}\''.format(
                self.name, self.parent.name))

    def detached(self):
        if self.logger:
            self.logger.update()


if __name__ == '__main__':
    class Test(Modular):
        def __init__(self):
            Modular.__init__(self, 'Test')

    t = Test()
    with t.logger.error('Hello :)', tag='test'):
        t.logger.error('Hello :)', tag='test')

