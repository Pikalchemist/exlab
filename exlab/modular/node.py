

class Node(object):
    def __init__(self, host, parent=None):
        self.host = host
        self._counter = None

        # Hierarchy
        self.children = None
        self.parent = None
        if parent is not None and not isinstance(parent, Node):
            parent = parent.host
        self.attach(parent)
    
    def __repr__(self):
        return f'{self.__class__.__name__}:{self.host}'

    def attach(self, parent):
        if parent is None or parent == self:
            return
        if self.parent:
            self.detached()
            if self.parent.children is not None:
                self.parent.children.remove(self)
        if parent.children is not None:
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
    
    @property
    def time(self):
        counter = self.counter
        if not counter:
            return -1
        return counter.t


class NodeWithChildren(Node):
    def __init__(self, host, parent=None):
        super().__init__(host, parent)
        self.children = set()
    
    def add_child(self, node):
        if node is None:
            return
        if node.parent:
            node.detached()
            if node.parent.children is not None:
                node.parent.children.remove(node)
        self.children.add(node)
        node.parent = self
        node.attached()

    def all_children(self):
        children = set()
        for child in self.children:
            children.add(child)
            children |= child.all_children
        return children
