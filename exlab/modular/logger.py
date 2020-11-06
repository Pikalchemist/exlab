from exlab.utils.text import Colors
from exlab.utils.io import parameter
from enum import Enum

from tabulate import tabulate
import coloredlogs
import logging
import sys


# class AllLogger(object):
#     def __init__(self, logger):
#         self.logger = logger

# loggers = {}


# def getLogger(name, *args, **kwargs):
#     kwargs['name'] = name
#     if name not in loggers:
#         loggers[name] = Logger(*args, **kwargs)
#     logger = loggers[name]

#     return Logger(proxy=logger, *args, **kwargs)


# class LoggerGroup(object):
#     def __init__(self, group):
#         self.group = group
    
#     def 


def logger():
    return Logger.instance()


class LoggerKind(Enum):
    RECORD = 0
    DISPLAY = 1
    SAV = 2


class Logger(object):
    DEBUG2 = 5
    TAG_SEPARATOR = '.'

    _instance = None

    def __init__(self):
        # tagLevels = {tag: (recording, to console, to file)}
        self.tagLevels = {'': [logging.DEBUG, logging.INFO, -1]}
        self.name = 'exlogger'
        self.events = []

        self.loggerTerminal = self.createLogger(f'{self.name}:c')
        self.loggerFile = self.createLogger(f'{self.name}:f')
        self.enableTerminal()
    
    @classmethod
    def instance(cls):
        if not cls._instance:
            cls._instance = Logger()
        return cls._instance
    
    def createLogger(self, name):
        logger = logging.getLogger(name)

        def dc(self):
            return None
        logger.__deepcopy__ = dc
        return logger

    def display(self, search=None, tag=None, style='html'):
        # data = [[colored(d, event.color(), style=style)
        #          for d in event.data()] for event in events]

        events = self.events
        if search:
            events = filter(lambda d: d.matches(search=search), events)
        if tag:
            events = filter(lambda d: d.matches(tag=tag), events)

        data = [event.data() for event in events]

        headers = ('Time', 'Level', 'Tag', 'Emitter', 'Message')
        if style == 'html':
            contents = tabulate(data, headers=headers, tablefmt="html")
            contents = contents.replace(
                '<td>', '<td style="text-align: left;">')
            from IPython.core.display import display, HTML
            display(HTML(contents))
        else:
            return tabulate(data, headers=headers, tablefmt="html")

    def matchingTag(self, tag):
        found = None
        depth = 0
        for key, value in self.tagLevels.items():
            if tag.startswith(key) and key.count(self.TAG_SEPARATOR) >= depth:
                found = (key, value)
                depth = key.count(self.TAG_SEPARATOR)
        return found

    def setLevel(self, level, tagFilter='', type_=0):
        if tagFilter not in self.tagLevels:
            self.tagLevels[tagFilter] = list(self.tagLevels[''])
        self.tagLevels[tagFilter][type_] = level

    def setRecordLevel(self, level, tagFilter=''):
        self.setLevel(level, tagFilter, 0)

    def setDisplayLevel(self, level, tagFilter=''):
        self.setLevel(level, tagFilter, 1)

    def setSaveLevel(self, level, tagFilter=''):
        self.setLevel(level, tagFilter, 2)
    
    def recordDebug(self, tagFilter=''):
        self.setRecordLevel(logging.DEBUG, tagFilter)

    def recordDebug2(self, tagFilter=''):
        self.setRecordLevel(Logger.DEBUG2, tagFilter)
    
    def displayDebug(self, tagFilter=''):
        self.setDisplayLevel(logging.DEBUG, tagFilter)

    def displayDebug2(self, tagFilter=''):
        self.setDisplayLevel(Logger.DEBUG2, tagFilter)
    
    def addEvent(self, msg, level, *args, **kwargs):
        modular = kwargs.get('module')
        event = Event(msg, level, modular.counter.t if modular and modular.counter else 0, modular, kwargs.get('tag', ''))
        self.events.append(event)
        return event

    def log(self, msg, level, *args, **kwargs):
        tag = kwargs.pop('tag', '').lower()
        _, levels = self.matchingTag(tag)

        # Recording (to memory)
        if level >= levels[0] and levels[0] >= 0:
            self.addEvent(msg, level, *args, tag=tag, **kwargs)
        kwargs.pop('module', '')

        tagStr = f'[{tag}] ' if tag else ''
        # Displaying
        if level >= levels[1] and levels[1] >= 0:
            self.loggerTerminal.log(level, f'{tagStr}{msg}', *args, **kwargs)
        # Saving (to file)
        if level >= levels[2] and levels[2] >= 0:
            pass
            # self.loggerTerminal.log(level, f'{tagStr}{msg}', *args, **kwargs)
    
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
    
    def enableTerminal(self):
        if not self.loggerTerminal.handlers:
            sh = logging.StreamHandler()
            sh.setLevel(1)
            self.loggerTerminal.addHandler(sh)

            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            sh.setFormatter(formatter)

            coloredlogs.install(level=1, logger=self.loggerTerminal)
    
    def disable_terminal(self):
        if self.loggerTerminal.handlers:
            self.loggerTerminal.handlers = []


class ProxyLogger(object):
    def __init__(self, module=None, tag=''):
        self.module = module
        self.tag = tag.lower()
    
    def display(self, search=None, tag=None, style='html'):
        logger().display(search=search, tag=self.tag, style=style)

    def setLevel(self, level, tagFilter=None, type_=0):
        logger().setLevel(level, parameter(tagFilter, self.tag), type_)

    def setRecordLevel(self, level, tagFilter=None):
        self.setLevel(level, tagFilter, 0)

    def setDisplayLevel(self, level, tagFilter=None):
        self.setLevel(level, tagFilter, 1)

    def setSaveLevel(self, level, tagFilter=None):
        self.setLevel(level, tagFilter, 2)

    def recordDebug(self, tagFilter=None):
        self.setRecordLevel(logging.DEBUG, tagFilter)

    def recordDebug2(self, tagFilter=None):
        self.setRecordLevel(Logger.DEBUG2, tagFilter)

    def displayDebug(self, tagFilter=None):
        self.setDisplayLevel(logging.DEBUG, tagFilter)

    def displayDebug2(self, tagFilter=None):
        self.setDisplayLevel(Logger.DEBUG2, tagFilter)

    def log(self, msg, level, *args, **kwargs):
        if 'tag' not in kwargs:
            kwargs['tag'] = self.tag
        if self.module:
            kwargs['module'] = self.module
        logger().log(msg, level, *args, **kwargs)
    
    def debug2(self, msg, *args, **kwargs):
        return self.log(msg, Logger.DEBUG2, *args, **kwargs)

    def debug(self, msg, *args, **kwargs):
        return self.log(msg, logging.DEBUG, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        return self.log(msg, logging.INFO, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        return self.log(msg, logging.WARNING, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        return self.log(msg, logging.ERROR, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        return self.log(msg, logging.CRITICAL, *args, **kwargs)


class Event(object):
    """
    A text event
    """
    number = 0

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

    def matches(self, search=None, tag=None):
        if search:
            return sum(search in str(data) for data in self.data()) > 0
        if tag:
            return self.tag.startswith(tag)
        return False

    def data(self):
        name = self.emitter.name if self.emitter else ''
        return (self.time, logging.getLevelName(self.level), self.tag, name, self.message)

    def __repr__(self):
        return f'@{self.time} [{self.tag}] {self.message}'



# class LoggingKind(Enum):
#     FILE = 0
#     EVENTS = 1
#     TERMINAL = 2


# class Logger(object):
#     DEBUG2 = 5

#     _main = None
 
#     def __init__(self, module=None, name='', tag='', proxy=None):
#         self.module = module
#         self.proxy = proxy
#         self.tag = tag

#         if self.proxy:
#             self.name = name
#         else:
#             self.name = name if name else ('m:{}'.format(
#                 self.module.name) if self.module else '')

#             self.events = {}
#             self.current_event = None
#             self.level = {}
#             self.default_level()

#             self.update()
#             self.enable_terminal()
        
#     def update(self):
#         if self.proxy:
#             return

#         if not self.module or self.module.root is self.module:
#             self.root = self
#         else:
#             self.root = self.module.root.logger

#         if self.root == self:
#             self.logger_terminal = self.create_logger('{}:c'.format(self.name))
#             self.logger_file = self.create_logger('{}:f'.format(self.name))

#     # def post_init(self):
#     #     if self.module.rootModule() == self.module:
#     #         self.__class__._main = self

#     def enable_terminal(self):
#         if self.proxy:
#             self.proxy.enable_terminal()
#         elif self.root is not self:
#             self.root.enable_terminal()
#         elif not self.logger_terminal.handlers:
#             sh = logging.StreamHandler()
#             sh.setLevel(1)
#             self.logger_terminal.addHandler(sh)

#             formatter = logging.Formatter(
#                 '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
#             sh.setFormatter(formatter)

#             coloredlogs.install(level=1, logger=self.logger_terminal)
    
#     def disable_terminal(self):
#         if self.proxy:
#             self.proxy.enable_terminal()
#         elif self.root is not self:
#             self.root.enable_terminal()
#         elif self.logger_terminal.handlers:
#             self.logger_terminal.handlers = []
    
#     def enable_file(self, filename):
#         if self.proxy:
#             self.proxy.enable_terminal()
#         elif self.root is not self:
#             self.root.enable_terminal()
#         elif not self.logger_file.handlers:
#             pass

#     def setLevel(self, level, kind=LoggingKind.TERMINAL):
#         if self.proxy:
#             self.proxy.setLevel(level, kind)
#         else:
#             self.level[kind] = level

#     def enable_debug(self, kind=LoggingKind.TERMINAL):
#         self.setLevel(logging.DEBUG, kind=kind)

#     def enable_debug2(self, kind=LoggingKind.TERMINAL):
#         self.setLevel(self.DEBUG2, kind=kind)

#     def default_level(self):
#         self.level[LoggingKind.EVENTS] = logging.DEBUG
#         self.level[LoggingKind.FILE] = logging.INFO
#         self.level[LoggingKind.TERMINAL] = logging.INFO

#     def create_logger(self, name):
#         logger = logging.getLogger(name)

#         def dc(self):
#             return None
#         logger.__deepcopy__ = dc
#         return logger

#     # def display_events(self, search=None, events=None, style='html'):
#     #     events = events if events else self.events
#     #     if isinstance(events, dict):
#     #         events = [event for _, d in events.items() for event in d]
#     #     data = [[colored(d, event.color(), style=style)
#     #              for d in event.data()] for event in events]
#     #     if search:
#     #         data = filter(lambda x: sum(
#     #             [search in str(d) for d in x]) > 0, data)
#     #     headers = ('time', 'Level', 'TAG', 'Emitter', 'Message')
#     #     if style == 'html':
#     #         contents = tabulate(data, headers=headers, tablefmt="html")
#     #         contents = contents.replace(
#     #             '<td>', '<td style="text-align: left;">')
#     #         from IPython.core.display import display, HTML
#     #         display(HTML(contents))
#     #     else:
#     #         return tabulate(data, headers=headers, tablefmt="html")

#     # @classmethod
#     # def init_loggers(cls):
#     #     logger = logging.getLogger('main')
    
#     #     sh = logging.StreamHandler()
#     #     sh.setLevel(logging.ERROR)
#     #     logger.addHandler(sh)

#     #     # coloredlogs.install(level='DEBUG', logger=logger)

#     #     logger.info("Logger started")

#     # @classmethod
#     # def main(cls):
#     #     return cls._main

#     def log(self, msg, level, *args, **kwargs):
#         if self.proxy:
#             kwargs['tag'] = kwargs.get('tag', self.tag)
#             return self.proxy.log(msg, level, *args, **kwargs)

#         tag = kwargs.pop('tag', '').upper()
#         tag = tag if tag else self.tag

#         tag_str = '[{}] '.format(tag) if tag else ''
#         if level >= self.level[LoggingKind.TERMINAL]:
#             self.root.logger_terminal.log(
#                 level, '{}{}'.format(tag_str, msg), *args, **kwargs)
#         if level >= self.level[LoggingKind.FILE]:
#             self.root.logger_file.log(
#                 level, '{}{}'.format(tag_str, msg), *args, **kwargs)

#         if self.module and level >= self.level[LoggingKind.EVENTS]:
#             event = Event(msg, level, self.module.time,
#                           emitter=self.module, tag=tag)

#             self.root.record_event(event)

#             return event

#     def record_event(self, event):
#         assert self.module.logger == self
#         if event.time not in self.events.keys():
#             self.events[event.time] = []
#         self.events[event.time].append(event)

#     def debug2(self, msg, *args, **kwargs):
#         return self.log(msg, self.DEBUG2, *args, **kwargs)

#     def debug(self, msg, *args, **kwargs):
#         return self.log(msg, logging.DEBUG, *args, **kwargs)

#     def info(self, msg, *args, **kwargs):
#         return self.log(msg, logging.INFO, *args, **kwargs)

#     def warning(self, msg, *args, **kwargs):
#         return self.log(msg, logging.WARNING, *args, **kwargs)

#     def error(self, msg, *args, **kwargs):
#         return self.log(msg, logging.ERROR, *args, **kwargs)

#     def critical(self, msg, *args, **kwargs):
#         self.log(msg, logging.CRITICAL, *args, **kwargs)
#         sys.exit(1)


# class Event(object):
#     """
#     A text event
#     """
#     number = 0

#     EVENT_COLOR = {
#         Logger.DEBUG2: Colors.MAGENTA,
#         logging.DEBUG: Colors.GREEN,
#         logging.INFO: Colors.NORMAL,
#         logging.WARNING: Colors.YELLOW,
#         logging.ERROR: Colors.RED,
#         logging.CRITICAL: Colors.RED,
#     }

#     def __init__(self, message, level, time, emitter, tag=''):
#         """
#         :param kind: EventKind of the event
#         :param time: time interval during which the event happened
#         :param parent: a parent Event being the precessor of the current one
#         :param emitter: the Module that has emitted the event
#         """
#         self.message = message
#         self.level = level
#         self.time = time
#         self.emitter = emitter
#         self.tag = tag

#         self.id = Event.number
#         Event.number += 1

#         self.parent = self.emitter.logger.current_event
#         self.children = set()
#         if self.parent:
#             self.parent.children.add(self)

#     # def primary_key(self):
#     #     return self.id

#     # def _serialize(self, options):
#     #     dict_ = Serializer.serialize(self, ['level', 'message', 'time'], ['parent', 'emitter'])
#     #     return dict_

#     # def data(self):
#     #     return [self.time, logging.getLevelName(self.level), self.tag, self.emitter.moduleName, self.message]

#     # def color(self):
#     #     return self.EVENT_COLOR[self.level]

#     def __enter__(self):
#         self.emitter.logger.current_event = self

#     def __leave__(self):
#         self.emitter.logger.current_event = self.parent

#     def __repr__(self):
#         return "@{} {} [{}] {}".format(self.time, self.emitter.name, self.tag, self.message)
