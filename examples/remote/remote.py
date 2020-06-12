from exlab.interface.graph import Graph
from exlab.lab.counter import EpisodeAbsoluteIterationCounter
from exlab.modular.module import Module
from exlab.modular.syncable import Syncable, manage
from exlab.formal.parameter import HyperParameter

import numpy as np

xg = Graph()


class TestRemote(Module):
    def __init__(self):
        super().__init__()

        manage(self).attach_counter(EpisodeAbsoluteIterationCounter())

        self.agent = Agent()
        manage(self).make_accessible(self.agent)

    def step(self):
        self.agent.step()
        manage(self).counter.next_iteration()


class Agent(Syncable):
    K = 0.01

    # register_hyperparameter(Agent, K, help='Growing rate of each agent += at each timestamp',
    #                         range='positive', how_to_choose='arbitrary')

    def __init__(self):
        super().__init__()
        self.growing_rate = 1

        self.age = 20
        self.ages = []

        manage(self).track(self.age, self.ages)
        manage(self).make_accessible(self.age, editable=True)

        manage(self).set_hyperparameter(self.growing_rate, help_='Growing rate of each agent += at each timestamp')
        manage(self).set_hyperparameter(self.K, help_='Growing rate of each agent += at each timestamp', range_='positive', how_to_choose='arbitrary')

        # self.a = np.random.uniform(0, 1, 10)
        # self.salaries = self.sync.track
        # self.remote.sync('a', index=EpisodeAbsoluteIterationCounter.EPISODE)

    def step(self):
        print(f'Step {self.age}')
        self.age += self.growing_rate + self.age * self.K
        self.ages.append(self.age)
        if len(self.ages) > 2:
            # self.ages.remove(self.ages[0])
            self.ages.pop()
            # self.ages = self.ages[1:]

    # @remote.graph
    def view_age(self, graph):
        graph.plot(self.ages)


tr = TestRemote()
tr.step()
tr.step()
tr.step()
tr.step()

print(manage(tr.agent).get_tracking(tr.agent.age).records)
print(manage(tr.agent).get_tracking(tr.agent.age).objects)
print(manage(tr.agent).get_tracking(tr.agent.age).attached)

print(manage(tr.agent).get_tracking(tr.agent.ages).records)
print(manage(tr.agent).get_tracking(tr.agent.ages).objects)
print(manage(tr.agent).get_tracking(tr.agent.ages).attached)

print(tr.agent.ages._tracking.records)
print(tr.agent.ages._tracking.objects)
print(tr.agent.ages._tracking.attached)

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
