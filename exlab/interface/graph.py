# from exlab.remote.server import Server
import matplotlib as mpl
import matplotlib.pyplot as plt


def display(graph):
    return Visual().display(graph)


class Visual(object):
    def __init__(self, server=None):
        # self.server = server if server else Server()
        pass

    def display(self, graph):
        self.fig = plt.figure()
        graph.display(self)


class Graph(object):
    def __init__(self, *items):
        super().__init__()
        self.items = list(items)
    
    def __add__(self, other):
        return self.__class__(*(self.items + other.items))
    
    def display(self, visual):
        visual.ax = visual.fig.add_subplot(1, 1, 1)
        visual.ax.yaxis.set_major_formatter(
            mpl.ticker.StrMethodFormatter('{x:,.3f}'))
        for item in self.items:
            item.display(visual)
    
    def plot(self, *args, **kwargs):
        self.items.append(PlotItem(*args, **kwargs))


class GraphItem(object):
    def __init__(self):
        pass

    def display(self, visual):
        pass


class PlotItem(GraphItem):
    def __init__(self, *data, **options):
        super().__init__()
        self.data = data
        self.dim = len(self.data)
        self.options = options
    
    def display(self, visual):
        plt.xlabel('Iteration')
        if self.dim == 1:
            visual.ax.plot(self.data[0])
        elif self.dim == 2:
            visual.ax.plot(self.data[0], self.data[1])
