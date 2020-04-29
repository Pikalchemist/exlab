from exlab.utils.io import Colors

import coloredlogs
import logging
import sys


class Logger(object):
    DEBUG2 = 5

    _main = None

    def __init__(self, module):
        self.module = module

        self.logger = self.create_logger(module.name)

        self.events = {}
        self.current_event = None

        self.console_handler = None
        self.console_enable()

        self.default_level()

    # def post_init(self):
    #     if self.module.rootModule() == self.module:
    #         self.__class__._main = self

    def console_enable(self):
        self.console_handler = logging.StreamHandler()
        self.console_handler.setLevel(logging.ERROR)
        self.logger.addHandler(self.console_handler)

        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.console_handler.setFormatter(formatter)

        coloredlogs.install(level='DEBUG', logger=self.logger)

    def setLevel(self, level):
        self.save_level = level

    def enable_debug(self):
        self.save_level = logging.DEBUG

    def enable_debug2(self):
        self.save_level = self.DEBUG2

    def default_level(self):
        self.save_level = logging.INFO

    def create_logger(self, name):
        logger = logging.getLogger(name)

        def dc(self):
            return None
        logger.__deepcopy__ = dc
        return logger

    # def display_events(self, search=None, events=None, style='html'):
    #     events = events if events else self.events
    #     if isinstance(events, dict):
    #         events = [event for _, d in events.items() for event in d]
    #     data = [[colored(d, event.color(), style=style)
    #              for d in event.data()] for event in events]
    #     if search:
    #         data = filter(lambda x: sum(
    #             [search in str(d) for d in x]) > 0, data)
    #     headers = ('time', 'Level', 'TAG', 'Emitter', 'Message')
    #     if style == 'html':
    #         contents = tabulate(data, headers=headers, tablefmt="html")
    #         contents = contents.replace(
    #             '<td>', '<td style="text-align: left;">')
    #         from IPython.core.display import display, HTML
    #         display(HTML(contents))
    #     else:
    #         return tabulate(data, headers=headers, tablefmt="html")

    # @classmethod
    # def init_loggers(cls):
    #     logger = logging.getLogger('main')
    
    #     sh = logging.StreamHandler()
    #     sh.setLevel(logging.ERROR)
    #     logger.addHandler(sh)

    #     # coloredlogs.install(level='DEBUG', logger=logger)

    #     logger.info("Logger started")

    # @classmethod
    # def main(cls):
    #     return cls._main

    def log(self, msg, level, *args, **kwargs):
        tag = kwargs.pop('tag', '').upper()
        self.logger.log(level, '[{}] {}'.format(tag, msg), *args, **kwargs)

        if level >= self.save_level:
            root = self.module.root()
            event = Event(msg, level, root.time, emitter=self.module, tag=tag)

            self.module.logger.record_event(event)

            return event

    def record_event(self, event):
        assert self.module.logger == self
        if event.time not in self.events.keys():
            self.events[event.time] = []
        self.events[event.time].append(event)

    def debug2(self, msg, *args, **kwargs):
        return self.log(msg, self.DEBUG2, *args, **kwargs)

    def debug(self, msg, *args, **kwargs):
        return self.log(msg, logging.DEBUG, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        return self.log(msg, logging.INFO, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        return self.log(msg, logging.WARNING, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        return self.log(msg, logging.ERROR, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        self.log(msg, logging.CRITICAL, *args, **kwargs)
        sys.exit(1)


class Event(object):
    """
    A text event
    """
    number = 0

    EVENT_COLOR = {
        Logger.DEBUG2: Colors.MAGENTA,
        logging.DEBUG: Colors.GREEN,
        logging.INFO: Colors.NORMAL,
        logging.WARNING: Colors.YELLOW,
        logging.ERROR: Colors.RED,
        logging.CRITICAL: Colors.RED,
    }

    def __init__(self, message, level, time, emitter, tag=''):
        """
        :param kind: EventKind of the event
        :param time: time interval during which the event happened
        :param parent: a parent Event being the precessor of the current one
        :param emitter: the Module that has emitted the event
        """
        self.message = message
        self.level = level
        self.time = time
        self.emitter = emitter
        self.tag = tag

        self.id = Event.number
        Event.number += 1

        self.parent = self.emitter.logger.current_event
        self.children = set()
        if self.parent:
            self.parent.children.add(self)

    # def primary_key(self):
    #     return self.id

    # def _serialize(self, options):
    #     dict_ = Serializer.serialize(self, ['level', 'message', 'time'], ['parent', 'emitter'])
    #     return dict_

    # def data(self):
    #     return [self.time, logging.getLevelName(self.level), self.tag, self.emitter.moduleName, self.message]

    # def color(self):
    #     return self.EVENT_COLOR[self.level]

    def __enter__(self):
        self.emitter.logger.current_event = self

    def __leave__(self):
        self.emitter.logger.current_event = self.parent

    def __repr__(self):
        return "@{} {} [{}] {}".format(self.time, self.emitter.name, self.tag, self.message)
