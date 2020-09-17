from exlab.utils.text import Colors
from enum import Enum

import coloredlogs
import logging
import sys


# class AllLogger(object):
#     def __init__(self, logger):
#         self.logger = logger

loggers = {}


def getLogger(name, *args, **kwargs):
    kwargs['name'] = name
    if name not in loggers:
        loggers[name] = Logger(*args, **kwargs)
    logger = loggers[name]

    return Logger(proxy=logger, *args, **kwargs)


# class LoggerGroup(object):
#     def __init__(self, group):
#         self.group = group
    
#     def 


class LoggingKind(Enum):
    FILE = 0
    EVENTS = 1
    TERMINAL = 2


class Logger(object):
    DEBUG2 = 5

    _main = None
 
    def __init__(self, module=None, name='', tag='', proxy=None):
        self.module = module
        self.proxy = proxy
        self.tag = tag

        if self.proxy:
            self.name = name
        else:
            self.name = name if name else ('m:{}'.format(
                self.module.name) if self.module else '')

            self.events = {}
            self.current_event = None
            self.level = {}
            self.default_level()

            self.update()
            self.enable_terminal()
        
    def update(self):
        if self.proxy:
            return

        if not self.module or self.module.root is self.module:
            self.root = self
        else:
            self.root = self.module.root.logger

        if self.root == self:
            self.logger_terminal = self.create_logger('{}:c'.format(self.name))
            self.logger_file = self.create_logger('{}:f'.format(self.name))

    # def post_init(self):
    #     if self.module.rootModule() == self.module:
    #         self.__class__._main = self

    def enable_terminal(self):
        if self.proxy:
            self.proxy.enable_terminal()
        elif self.root is not self:
            self.root.enable_terminal()
        elif not self.logger_terminal.handlers:
            sh = logging.StreamHandler()
            sh.setLevel(1)
            self.logger_terminal.addHandler(sh)

            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            sh.setFormatter(formatter)

            coloredlogs.install(level=1, logger=self.logger_terminal)
    
    def disable_terminal(self):
        if self.proxy:
            self.proxy.enable_terminal()
        elif self.root is not self:
            self.root.enable_terminal()
        elif self.logger_terminal.handlers:
            self.logger_terminal.handlers = []
    
    def enable_file(self, filename):
        if self.proxy:
            self.proxy.enable_terminal()
        elif self.root is not self:
            self.root.enable_terminal()
        elif not self.logger_file.handlers:
            pass

    def setLevel(self, level, kind=LoggingKind.TERMINAL):
        if self.proxy:
            self.proxy.setLevel(level, kind)
        else:
            self.level[kind] = level

    def enable_debug(self, kind=LoggingKind.TERMINAL):
        self.setLevel(logging.DEBUG, kind=kind)

    def enable_debug2(self, kind=LoggingKind.TERMINAL):
        self.setLevel(self.DEBUG2, kind=kind)

    def default_level(self):
        self.level[LoggingKind.EVENTS] = logging.DEBUG
        self.level[LoggingKind.FILE] = logging.INFO
        self.level[LoggingKind.TERMINAL] = logging.INFO

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
        if self.proxy:
            kwargs['tag'] = kwargs.get('tag', self.tag)
            return self.proxy.log(msg, level, *args, **kwargs)

        tag = kwargs.pop('tag', '').upper()
        tag = tag if tag else self.tag

        tag_str = '[{}] '.format(tag) if tag else ''
        if level >= self.level[LoggingKind.TERMINAL]:
            self.root.logger_terminal.log(
                level, '{}{}'.format(tag_str, msg), *args, **kwargs)
        if level >= self.level[LoggingKind.FILE]:
            self.root.logger_file.log(
                level, '{}{}'.format(tag_str, msg), *args, **kwargs)

        if self.module and level >= self.level[LoggingKind.EVENTS]:
            event = Event(msg, level, self.module.time,
                          emitter=self.module, tag=tag)

            self.root.record_event(event)

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
