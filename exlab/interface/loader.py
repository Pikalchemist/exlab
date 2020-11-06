'''
    Author: Alexandre Manoury
    Python Version: 3.6
'''
from exlab.lab.database import Database
from exlab.utils.io import mkdir

import exlab.modular.logger as exlogger

from pathlib import Path
import sys
import os


logger = exlogger.ProxyLogger(tag='LOAD')
# logger.displayDebug2()


def register_sourcepath(sourcepath):
    Loader.instance().add_source(sourcepath)


class MissingConfig(Exception):
    pass


class Loader(object):
    """
    Singleton instance managing all the loadable data
    """
    _instance = None

    def __init__(self):
        if self._instance is not None:
            raise Exception('Loader cannot be instantiated twice!')

        # self.sourcepath = set()
        logger.info('Loader has been init')

    @classmethod
    def instance(cls) -> 'Loader':
        """
        Get instance
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    @property
    def sourcepath(self):
        return [Path(p) for p in sys.path]
    
    def add_source(self, sourcepath):
        if type(sourcepath) is not list:
            sourcepath = [sourcepath]

        added = []
        for path in sourcepath:
            if path:
                path = Path(path).resolve()
                if not path.is_dir:
                    path = path.parent
                if path not in self.sourcepath:
                    sys.path.insert(0, str(path))
                    added.append(path)
            elif path is None:
                logger.warning('Trying to add None path to the loader')

        if added:
            logger.info(
                f'Source folder(s) {added} has been added to the loader')

    # def register_default_sourcepath(self):
    #     self.add_source(Path.cwd())

    def class_path(self, obj):
        # if not self.sourcepath:
        #     self.register_default_sourcepath()

        path = Path(sys.modules[obj.__module__].__file__)

        for p in self.sourcepath:
            try:
                relative = path.relative_to(p)
                return str(relative.with_suffix('')).replace('/', '.').replace('\\', '.')
            except ValueError:
                pass
        raise Exception('Trying to save a python file not residing inside the source path.\n' +
                        'May be you have forgotten to update utils.loaders.sourcePath?\n' +
                        f'Path: {path}')
    

    def load(self, path, classname=None, imports=None):
        # if not self.sourcepath:
        #     self.register_default_sourcepath()
        if str(path).endswith('.py'):
            path = str(path)[:-len('.py')]

        logger.debug(
            f'Importing {classname} from {path}')
        filepath = Path(path.replace('.', '/')).with_suffix('.py')

        found = False
        for sp in self.sourcepath:
            if (sp / filepath).exists():
                found = True
        if not found:
            raise Exception(f'File \'{filepath}\' not found in the source path.\n' +
                            f'Currently: {map(str, self.sourcepath)}\n' +
                            'May be you have forgotten to update utils.loaders.sourcePath?')

        imports = imports if imports else [classname]
        module = __import__(path.replace('/', '.'), fromlist=imports)
        if not classname:
            return module
        return getattr(module, classname)

    def instantiate(self, path, classname=None, dict_={}, args=(), kwargs={}, serializer=None, imports=None):
        cls_ = self.load(path, classname=classname, imports=imports)
        if hasattr(cls_, '_deserialize'):
            obj = cls_.deserialize(dict_, serializer)
        else:
            obj = cls_(*args, **kwargs)
        return obj
    
    
    
    @staticmethod
    def find_file(filelist, prefix='', suffix=''):
        for file_ in filelist:
            if os.path.exists(os.path.join(prefix, file_, suffix)):
                return file_
        return None
