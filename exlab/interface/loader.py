'''
    Author: Alexandre Manoury
    Python Version: 3.6
'''
import exlab.modular.logger as exlogger

import sys
import os


logger = exlogger.getLogger('loader', tag='LOAD')
logger.enable_debug2()


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
        print('bloup')
        if self._instance is not None:
            raise Exception('Loader cannot be instantiated twice!')

        self.sourcepath = set()
        logger.info('Loader has been init')

    @classmethod
    def instance(cls, sourcepath=[]):
        """
        Get instance
        """
        if cls._instance is None:
            cls._instance = cls()
        cls._instance.add_source(sourcepath)
        return cls._instance
    
    def add_source(self, sourcepath):
        if type(sourcepath) is not list:
            sourcepath = [sourcepath]
        added = []
        for path in sourcepath:
            if path:
                self.sourcepath.add(path)
                added.append(path)
            elif path is None:
                logger.warning('Trying to add None path to the loader')

        if added:
            logger.info(
                'Source folder(s) {} has been added to the loader'.format(added))

    def class_path(self, obj):
        path = sys.modules[obj.__module__].__file__

        for p in self.sourcepath:
            if path.startswith(p):
                return path[len(p) + 1:].replace('/', '.').replace('\\', '.')
        raise Exception('Trying to save a python file not residing inside the source path.\n' +
                        'May be you have forgotten to update utils.loaders.sourcePath?\n' +
                        'Path: {}'.format(path))
    

    def load_type(self, path, cls_=None, imports=None):
        logger.debug(
            'Importing {} from {}'.format(cls_, path))
        path = os.path.splitext(path)[0]
        selectedName = None
        for sp in self.sourcepath:
            fullpath = os.path.join(sp, path.replace('.', '/') + '.py')
            if os.path.exists(fullpath):
                selectedName = path
        if not selectedName:
            raise Exception('File {} not found in the source path.\n'.format(path) +
                            'May be you have forgotten to update utils.loaders.sourcePath?')

        imports = imports if imports else [cls_]
        module = __import__(selectedName.replace('/', '.'), fromlist=imports)
        if not cls_:
            return module
        return getattr(module, cls_)
    
    @staticmethod
    def find_file(filelist, prefix='', suffix=''):
        for file_ in filelist:
            if os.path.exists(os.path.join(prefix, file_, suffix)):
                return file_
        return None
