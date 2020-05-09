from exlab.interface.graph import Graph
from exlab.lab.counter import EpisodeAbsoluteIterationCounter
from exlab.remote.remote import Syncable

import numpy as np

xg = Graph()


class TestRemote(Syncable):
    def __init__(self):
        super().__init__()
        # self.a = np.random.uniform(0, 1, 10)
        self.max_value = self._tracker.object(1)

        # self.remote.expose()
        self._remote.access('max_value', editable=True)
        # self.remote.sync('a', index=EpisodeAbsoluteIterationCounter.EPISODE)

    def step(self):
        self.max_value.track()

    # @remote.sync.attribute('a', EpisodeAbsoluteIterationCounter.EPISODE)
    # def sync_a(self):

    # @remote.graph
    # def view_a(self, graph):
    #     graph.plot(self.a)


tr = TestRemote()
print(tr.remote.syncs)

# print(a)

# xg.plot(a)
