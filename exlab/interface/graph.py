from exlab.interface.remote import Server


class Graph(object):
    def __init__(self, server=None):
        self.server = server if server else Server()