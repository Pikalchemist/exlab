'''
    Author: Alexandre Manoury
    Python Version: 3.6
'''


class Syncable(object):
    def __init__(self):
        self._remote = Syncable.Remote(self)
        self._tracker = Syncable.Tracker(self)


    class Remote(object):
        def __init__(self, parent):
            self.parent = parent
            self.syncs = []

        # def sync(self, *attributes, index=None):
        #     for attribute in attributes:
        #         self.syncs.append({attribute: True})

        def access(self, *attributes, editable=False, index=None):
            for attribute in attributes:
                if isinstance(attribute, Syncable):
                    

                self.syncs.append({attribute: Attribute(
                    attribute, editable=editable, index=index)})


    class Tracker(object):
        def __init__(self, parent):
            self.parent = parent

        def object(self, obj):
            return None


class Attribute(object):
    def __init__(self, name, editable=False, index=None):
        self.name = name
        self.editable = editable
        self.index = index
    
    def __repr__(self):
        return f'Attribute.{self.name}'
