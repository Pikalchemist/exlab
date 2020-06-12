'''
    Author: Alexandre Manoury
    Python Version: 3.6
'''

from exlab.modular.node import Node
from exlab.modular.attribute import Attribute
from exlab.interface.tracking import AttributeTracker, Tracking


class Syncable(object):
    def __init__(self, parent=None):
        self._exlab_manager = Syncable.Sync(self, parent)

    class Sync(Node):
        def __init__(self, host, parent):
            super().__init__(host, parent)

            self.attributes = {}
            self.trackings = {}
        
        # def attached(self):
        #     super()
        #     for tracking in self.trackings.values():
        #         tracking.attached()
        
        def get_attribute_name(self, attribute):
            attribute_id = id(attribute)
            # if attribute_id in self.ids:
            #     return self.ids[attribute_id]
            for key, value in self.host.__dict__.items():
                if id(value) == attribute_id:
                    # self.ids[attribute_id] = key
                    return key, False
            for key, tracking in self.trackings.items():
                if id(tracking.object) == attribute_id:
                    # self.ids[attribute_id] = key
                    return key, False
            for key, value in self.host.__class__.__dict__.items():
                if id(value) == attribute_id:
                    # self.ids[attribute_id] = key
                    return key, True
            return None, False

        # def sync(self, *attributes, index=None):
        #     for attribute in attributes:
        #         self.syncs.append({attribute: True})

        def attribute(self, name, is_class_attribute):
            if name not in self.attributes:
                self.attributes[name] = Attribute(name, is_class_attribute)
            return self.attributes[name]

        def make_accessible(self, *attributes, editable=False, index=None):
            for attribute in attributes:
                name, is_class_attribute = self.get_attribute_name(attribute)
                if name:
                    # if isinstance(attribute, Syncable):
                    #     attribute._exlab_manager.attach(self)
                    # if hasattr(obj, '_tracking'):
                    #     obj._tracking.

                    # Attribute(name, editable=editable, index=index)})
                    self.attribute(name, is_class_attribute).make_accessible(
                        editable=editable, index=index)

        # def track_manual(self, obj):
        #     return Tracker(self, obj)
        
        # def track_auto(self, obj):
        #     return AutoTracker(self, obj)
        
        def track(self, *attributes):
            for attribute in attributes:
                name, is_class_attribute = self.get_attribute_name(attribute)
                if is_class_attribute:
                    raise Exception(
                        'Cannot track class attribute, please use an instance attribute instead.')
                if name:
                    tracker = AttributeTracker(self, name, attribute)
                    self.trackings[name] = tracker

                    setattr(self.host, name, None)
                    setattr(self.host.__class__, name, property(tracker.getter, tracker.setter))

        def get_tracking(self, attribute):
            name, is_class_attribute = self.get_attribute_name(attribute)
            if is_class_attribute:
                raise Exception(
                    'Cannot track class attribute, please use an instance attribute instead.')
            if name and name in self.trackings:
                return self.trackings[name]._tracking
            return None

        def set_hyperparameter(self, *attributes, help_=None, range_=None, how_to_choose=None):
            for attribute in attributes:
                name, is_class_attribute = self.get_attribute_name(attribute)
                if name:
                    self.attribute(name, is_class_attribute).set_hyperparameter(
                        help_=help_, range_=range_, how_to_choose=how_to_choose)

def manage(instance):
    return instance._exlab_manager


# def track(instance, *attributes):
#     instance._sync.track(*attributes)


# def get_tracking(instance, attribute):
#     return instance._sync.get_tracking(attribute)


# def make_accessible(instance_or_class, *attributes, **kwargs):
#     instance_or_class._sync.make_accessible(*attributes, **kwargs)
