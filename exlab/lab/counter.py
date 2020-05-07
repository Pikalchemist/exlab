

class Counter(object):
    NO_PAST = 'Cannot go back in the past ! Create a new counter or a new experiment'
    NOT_MODIFIABLE = 'Cannot be modified, please create a new counter'

    def __init__(self, t=0):
        self._t = t
    
    @property
    def t(self):
        return self._t

    @t.setter
    def t(self, t):
        if t < self._t:
            raise ValueError(self.NO_PAST)
        self._t = t

    def next_timestep(self):
        self._t += 1

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


class NoCounter(Counter):
    pass


class IterationCounter(Counter):
    def __init__(self, iteration=0):
        super(IterationCounter, self).__init__()
        self._iteration = iteration
        self.t = iteration

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
    next_iteration_at_episode_end = False

    def __init__(self, iteration=0, episode=0):
        super(EpisodeAbsoluteIterationCounter, self).__init__(iteration)
        self._episode = episode

        # Stats
        self._last_iteration = 0
        self.iterations_by_episode = []

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
        super(EpisodeIterationCounter, self).__init__(iteration, episode)
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


c = EpisodeIterationCounter()
c.next_iteration()
c.next_iteration()
c.next_episode()
c.next_iteration()
c.next_episode()
c.next_iteration()

print(c.t)
print(c.episode)
print(c.iteration)
print(c.iterations_by_episode)
