from exlab.interface.graph import Graph
from exlab.lab.counter import EpisodeAbsoluteIterationCounter
from exlab.modular.module import Module
from exlab.modular.syncable import Syncable
from exlab.formal.parameter import HyperParameter

import numpy as np

xg = Graph()


class TestRemote(Module):
    def __init__(self):
        super().__init__()

        self._module.attach_counter(EpisodeAbsoluteIterationCounter())

        self.agent = Agent()
        self.sync.access('agent')

    def step(self):
        # self.agent.step()
        self._module.counter.next_iteration()


class Agent(Syncable):
    k = 0.01

    _ATTRIBUTES = {
        'k':                HyperParameter(help='Growing rate of each agent += at each timestamp', range='positive', how_to_choose='arbitrary')
        'growing_rate':     HyperParameter(help='Growing rate of each agent += at each timestamp', range='positive', how_to_choose='arbitrary')
    }

    def __init__(self):
        super().__init__()
        self.growing_rate = 1

        self.age = 20

        track(self, self.age)
        make_accessible(self.age, editable=True)

        # self.sync.make_accessible('age', editable=True)

        # self.a = np.random.uniform(0, 1, 10)
        # self.salaries = self.sync.track
        # self.remote.sync('a', index=EpisodeAbsoluteIterationCounter.EPISODE)
    
    @hyperparameter
    def growing_rate(self):

    # def step(self):
    #     self.age.object += self.GROWING_RATE

    # @remote.sync.attribute('a', EpisodeAbsoluteIterationCounter.EPISODE)
    # def sync_a(self):

    # @remote.graph
    # def view_a(self, graph):
    #     graph.plot(self.a)


tr = TestRemote()
# print(tr)
# print(tr.module.counter)
# print(tr.agent.sync.root)
# print(tr.agent.sync.counter)
# print()
# tr.step()
# tr.step()
# print(tr.agent.age)
# print(type(tr.agent.age))
# print(tr.agent.age._tracking.records)
# print(tr.sync.syncs)

# print(a)

# xg.plot(a)
