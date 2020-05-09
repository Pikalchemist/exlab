

class Tracking(object):
    ADD = 0
    DELETE = 0

    def __init__(self):
        pass


class TrackVariable(object):
    def __init__(self, obj):
        self.obj = obj
        self.tracker = Tracking()
    
    def update(self, obj):
        self.obj = obj


class TrackList(list):
    def __init__(self, *args):
        super().__init__(*args)
        self.tracking