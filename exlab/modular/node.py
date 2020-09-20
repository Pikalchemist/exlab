

class Node(object):
    _activated = None

    def __init__(self, host, parent=None):
        self.host = host
        self._counter = None
        self._serializer = None

        # Hierarchy
        self.children = None
        self.parent = None
        self.attach(parent)

    def __repr__(self):
        return f'{self.__class__.__name__}Manager:{self.host}'

    def activate(self):
        Node._activated = self
        self.attach_serializer()

    def attach(self, parent):
        if parent is not None and not isinstance(parent, Node):
            parent = parent._exlab_manager
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

    def attach_serializer(self, serializer=None):
        if serializer:
            self._serializer = serializer
        elif not self._serializer:
            from exlab.interface.serializer import Serializer
            self._serializer = Serializer()

    def attach_counter(self, counter):
        self._counter = counter
        self.activate()
    
    def parents(self):
        node = self
        parents = set([node])
        while node.parent:
            node = node.parent
            parents.add(node)
        return parents
    
    def effective_parent(self):
        if self.parent:
            return self.parent
        if not Node._activated or self in Node._activated.parents():
            return None
        return Node._activated

    @property
    def root(self):
        root = self
        while root.effective_parent():
            root = root.effective_parent()
        return root

    @property
    def counter(self):
        node = self
        while node.effective_parent():
            if node._counter:
                return node._counter
            node = node.effective_parent()
        return node._counter

    @property
    def serializer(self):
        node = self
        while node.effective_parent():
            node = node.effective_parent()
            if node._serializer:
                return node._serializer
        return node._serializer

    @property
    def time(self):
        counter = self.counter
        if not counter:
            return -1
        return counter.t
    
    @staticmethod
    def activated():
        return Node._activated


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
