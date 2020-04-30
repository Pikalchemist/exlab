'''
    Author: Alexandre Manoury
    Python Version: 3.6
'''
import sys
import os


class MissingConfig(Exception):
    pass


class Loader(object):
    """
    Singleton instance managing all the loadable data
    """
    def __init__(self, sourcepath):
        print('bloup')

        if type(sourcepath) is not list:
            sourcepath = [sourcepath]
        self.sourcepath = sourcepath
    
    def class_path(self, obj):
        path = sys.modules[obj.__module__].__file__

        for p, _ in self.sourcepath:
            if path.startswith(p):
                return path[len(p) + 1:].replace('/', '.').replace('\\', '.')
        raise Exception('Trying to save a python file not residing inside the source path.\n' +
                        'May be you have forgotten to update utils.loaders.sourcePath?\n' +
                        'Path: {}'.format(path))
    
    def load_type(self, path, cls_=None, imports=None):
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
