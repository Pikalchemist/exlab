import copy


class Tracking(object):
    CHANGE = 0
    ADD = 1
    DELETE = 2

    def __init__(self, tracker, host, save_initial_value=True):
        self.tracker = tracker
        self.host = host
        self.records = {}
        if save_initial_value:
            self.track()
    
    def track(self):
        self.event(Tracking.CHANGE, self.tracker._object)
    
    def event(self, event_type, key=None, element=None):
        counter = self.counter
        index = self.counter.t + 1 if counter is not None else -1
        if index not in self.records or event_type == Tracking.CHANGE:
            self.records[index] = []
        self.records[index].append((event_type, key, element))
    
    def attach(self, new_tracker):
        t = copy.copy(self)
        t.tracker = new_tracker
        return t

    @property
    def root(self):
        root = self.host
        while root.parent:
            root = root.parent
        return root

    @property
    def counter(self):
        return self.host.counter


class GenericTracker(object):
    def __init__(self, obj, host, tracking=None, save_initial_value=True):
        self._object = obj
        if tracking:
            self._tracking = tracking.attach(self)
            self._tracking.track()
        else:
            self._tracking = Tracking(
                self, host, save_initial_value=save_initial_value)


class Tracker(GenericTracker):
    def __init__(self, obj, host, tracking=None, save_initial_value=False):
        super().__init__(obj, host, tracking=tracking,
                         save_initial_value=save_initial_value)
    
    @property
    def object(self):
        return self._object
    
    @object.setter
    def object(self, obj):
        self.update(obj)

    def update(self, obj):
        self._object = obj
    
    def updated(self):
        pass
    
    def track(self):
        self._tracking.track()


class AutoTracker(Tracker):
    def __init__(self, obj, host, tracking=None, save_initial_value=True):
        super().__init__(obj, host, tracking=tracking,
                         save_initial_value=save_initial_value)

    def update(self, obj):
        self._object = obj
        self._tracking.track()

    def updated(self):
        self._tracking.track()


class ListTracker(list, GenericTracker):
    def __init__(self, list_, host, tracking=None, save_initial_value=True):
        list.__init__(self, list_)
        GenericTracker.__init__(self, self, host, tracking=tracking, save_initial_value=save_initial_value)

    def append(self, x):
        list.append(self, x)
        self._tracking.event(Tracking.ADD, len(self) - 1, x)
    
    def insert(self, i, x):
        list.insert(self, i, x)
        self._tracking.event(Tracking.ADD, i, x)
    
    def remove(self, x):
        i = list.index(x)
        list.remove(self, x)
        self._tracking.event(Tracking.DELETE, i)
    




# class WrapperAutoTracker(GenericTracker):
#     def __init__(self, obj, host, tracking=None):
#         super().__init__(obj, host, tracking=tracking)
#         # self.tracker = Tracking()
    
#     def __getattr__(self, name):
#         return getattr(self._obj, name)
    
#     def __deepcopy__(self, m):
#         pass

#     def __repr__(self):
#         return self._object.__repr__()

#     def __add__(self, o):
#         return self.__class__(self._tracking.host, self._object.__add__(o), tracking=self._tracking)


# class TrackList(list):
#     def __init__(self, *args):
#         super().__init__(*args)
#         self.tracking
