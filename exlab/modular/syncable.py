'''
    Author: Alexandre Manoury
    Python Version: 3.6
'''

from exlab.modular.node import Node
from exlab.interface.tracking import Tracker, AutoTracker


class Syncable(object):
    def __init__(self, parent=None):
        self._sync = Syncable.Sync(self, parent)

    class Sync(Node):
        def __init__(self, host, parent):
            super().__init__(host, parent)
            self.syncs = []

        # def sync(self, *attributes, index=None):
        #     for attribute in attributes:
        #         self.syncs.append({attribute: True})

        def make_accessible(self, *attributes, editable=False, index=None):
            for attribute in attributes:
                obj = getattr(self.host, attribute)
                if isinstance(obj, Syncable):
                    obj.sync.attach(self)
                # if hasattr(obj, '_tracking'):
                #     obj._tracking.

                self.syncs.append({attribute: Attribute(
                        attribute, editable=editable, index=index)})
        
        def track_manual(self, obj):
            return Tracker(self, obj)
        
        def track_auto(self, obj):
            return AutoTracker(self, obj)
        
        def track(self, obj):
            return self.track_auto(obj)

