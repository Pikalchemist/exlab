

class BaseCounter(object):
    NO_PAST = 'Cannot go back in the past! Create a new counter or a new experiment'
    NOT_MODIFIABLE = 'Cannot be modified, please create a new counter'
    NO_PARENT = 'Cannot sync counter of a module without parent!'

    T = 't'
    MODIFIABLE = True

    def __init__(self, t=0):
        self._t = t

    @property
    def t(self):
        return self._t
    
    @t.setter
    def t(self, t):
        if not self.MODIFIABLE:
            raise ValueError(self.MODIFIABLE)
        if t < self._t:
            raise ValueError(self.NO_PAST)
        self._t = t

    @property
    def last(self):
        return self._t - 1

    def __repr__(self):
        return f'(_t={self._t})'

    def __lt__(self, other):
        return self._t < other._t

    def __le__(self, other):
        return self._t <= other._t

    def __gt__(self, other):
        return self._t > other._t

    def __ge__(self, other):
        return self._t >= other._t

    def __eq__(self, other):
        return self._t == other._t

    def __ne__(self, other):
        return self._t != other._t


class Counter(BaseCounter):
    def next_timestep(self):
        self._t += 1


class NoCounter(Counter):
    pass


class AsyncCounter(BaseCounter):
    MODIFIABLE = False

    def __init__(self, module):
        super().__init__()
        self.node = module._exlab_manager
        self.sync()

    def sync(self):
        if self.node.parent is None:
            raise Exception(self.NO_PARENT)
        self._t = self.node.parent.counter.t


class IterationCounter(Counter):
    ITERATION = 'iteration'

    def __init__(self, iteration=0):
        super().__init__()
        self._iteration = iteration
        self.t = iteration
    
    def __repr__(self):
        return f'(iteration={self._iteration}, _t={self._t})'

    @property
    def iteration(self):
        return self._iteration

    @iteration.setter
    def iteration(self, iteration):
        self._iteration = iteration
        self.t = self._iteration

    def next_iteration(self):
        self.iteration += 1


class EpisodeAbsoluteIterationCounter(IterationCounter):
    EPISODE = 'epsiode'

    next_iteration_at_episode_end = False

    def __init__(self, iteration=0, episode=0):
        super().__init__(iteration)
        self._episode = episode

        # Stats
        self._last_iteration = 0
        self.iterations_by_episode = []
    
    def __repr__(self):
        return f'(episode={self._episode}, iteration={self._iteration}, _t={self._t})'

    @property
    def episode(self):
        return self._episode

    @episode.setter
    def episode(self, episode):
        if episode < self._episode:
            raise ValueError(self.NO_PAST)
        self._episode = episode

    def next_episode(self):
        if self.next_iteration_at_episode_end:
            self.next_iteration()
        self.episode += 1

        self.iterations_by_episode.append(
            self.iteration - self._last_iteration)
        self._last_iteration = self.iteration


class EpisodeIterationCounter(EpisodeAbsoluteIterationCounter):
    def __init__(self, t=0, iteration=0, episode=0):
        super().__init__(iteration, episode)
        self.t = t
    
    def next_iteration(self):
        self.next_timestep()
        self._iteration += 1

    def next_episode(self):
        if self.next_iteration_at_episode_end:
            self.next_iteration()
        self.next_timestep()

        self.iterations_by_episode.append(self.iteration)

        self._iteration = 0
        self._episode += 1
    
    @property
    def iteration(self):
        return self._iteration
    
    @property
    def episode(self):
        return self._episode

    @iteration.setter
    def iteration(self, iteration):
        raise Exception(self.NOT_MODIFIABLE)

    @episode.setter
    def episode(self, episode):
        raise Exception(self.NOT_MODIFIABLE)


# c = EpisodeIterationCounter()
# c.next_iteration()
# c.next_iteration()
# c.next_episode()
# c.next_iteration()
# c.next_episode()
# c.next_iteration()

# print(c.t)
# print(c.episode)
# print(c.iteration)
# print(c.iterations_by_episode)
