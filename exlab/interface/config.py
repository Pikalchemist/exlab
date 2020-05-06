from exlab.utils.path import ymlbpath, extpath
from exlab.utils.structure import get_sub_dict_path, get_dict_path, set_dict_path
from exlab.utils.io import shortid
from exlab.interface.loader import Loader
import exlab.modular.logger as exlogger

import argparse
import copy
import yaml
import os
import re


logger = exlogger.getLogger('config', tag='CONF')
logger.enable_debug2()


class LightConfig(dict):
    def __init__(self, dict_={}, data=None):
        super(LightConfig, self).__init__(dict_)
        self.data = data if data else dict_


class Config(LightConfig):
    MAX_MULTIVALUES = 100

    def __init__(self, basedir='', structure=None, top=True, relativedir='', topdir='', loader=None):
        super(Config, self).__init__()
        self.top = top
        self.structure = structure if structure else ConfigStructure()
        self.parameters = {}
        self.multivalues = {}

        self.basedir = basedir
        self.topdir = topdir if topdir else basedir
        self.relativedir = relativedir
    
        self.loader = loader

        logger.debug('#{} config file created, basedir {}'.format(
            shortid(self), self.basedir))

    def load_file(self, filename):
        logger.debug2('#{} load file {}'.format(shortid(self), filename))

        data = self._load_data_from_file(filename)
        self.update(data)
        self._load_parameters(filename)

    def _load_data_from_file(self, filename):
        filename = ymlbpath(self.basedir, filename)
        try:
            with open(filename) as f:
                data = yaml.load(f, Loader=yaml.FullLoader)
            self._walk_dict(data)
            return data
        except Exception as e:
            logger.warning('#{} cannot load data from {}: {}'.format(
                shortid(self), filename, e))
            return {}

    def load_args(self, argv, custom_argparse=False):
        logger.debug2(
            '#{} load input arguments {}'.format(shortid(self), argv))

        if argv:
            arg = argv[0]
            if '=' not in arg and not arg.startswith('-'):
                self.load_file(argv.pop(0))

        other_args = []
        for arg in argv:
            if '=' in arg:
                path, value = arg.split('=')[:2]
                if ',' in value:
                    self.multivalues[path] = value.split(',')
                    value = value.split(',')[0]
                set_dict_path(self, path, value)
            else:
                other_args.append(arg)

        self._load_parameters()

        if custom_argparse:
            return other_args
        
        parser = argparse.ArgumentParser(description='EXLab')
        parser.add_argument('--verbose', '-v', action='count', default=0)
        parsed = parser.parse_args(other_args)

        return parsed
    
    def grid(self):
        confs = []

        for key, values in self.multivalues.items():
            if confs:
                confs = [dict(conf, key=value) for value in values for conf in confs]
            else:
                confs = [{key: value} for value in values]

        if len(confs) > self.MAX_MULTIVALUES:
            raise Exception('Too many ({}/{})'.format(len(confs), self.MAX_MULTIVALUES))
    
        if not confs:
             # Default configuration
            confs.append({})
    
        configs = []
        for conf in confs:
            configs.append(self.copy(conf))

        return configs
    
    def copy(self, conf={}):
        config = copy.deepcopy(self)
        for key, value in conf.items():
            set_dict_path(config, key, value)
        return config

    def _load_parameters(self, filename=None):
        parameters = self.structure.retrieve_parameters(self.top, os.path.join(self.relativedir, filename) if filename else None)
        logger.debug2(
            '#{} parameters {}'.format(shortid(self), parameters))

        for key, parameter in parameters.items():
            try:
                sdict, skey = get_sub_dict_path(self, key)
                if skey in sdict:
                    # Key
                    if parameter._key:
                        (tkey, tfilename) = parameter._key
                        fns = tfilename if tfilename else [None]
                        for fn in fns:
                            if isinstance(sdict[skey], (str, int)):
                                if fn:
                                    config = Config(self.topdir, structure=self.structure, top=False)
                                    config.load_file(fn)
                                else:
                                    config = self
                                try:
                                    sdict[skey] = get_dict_path(config, tkey).get(sdict[skey])
                                    break
                                except Exception:
                                    pass

                    # File
                    if parameter._file:
                        if isinstance(sdict[skey], (str, int)):
                            folder = Loader.find_file(
                                parameter._file, prefix=self.basedir, suffix=extpath(sdict[skey], 'yml'))
                            config = Config(os.path.join(
                                self.basedir, folder),
                                topdir=self.topdir,
                                relativedir=os.path.join(self.relativedir, folder),
                                structure=self.structure, top=False)
                            config.load_file(sdict[skey])
                            sdict[skey] = config
            except KeyError:
                continue

    def populate(self, loader=None):
        loader = loader if loader else self.loader
        if not loader:
            loader = Loader.instance(self.basedir)
        self.loader = loader

        self.data = copy.deepcopy(self)
        self.update(self._walk_populate(self))

    def _walk_dict(self, data):
        if type(data) is dict:
            for _, value in data.items():
                self._walk_dict(value)
            if '__import__' in data:
                filename = data['__import__']
                logger.debug2(
                    '#{} import from {}'.format(shortid(self), filename))

                data.clear()
                data.update(self._load_data_from_file(filename))
        elif type(data) in (list, tuple):
            for value in data:
                self._walk_dict(value)
    
    def _walk_populate(self, data):
        if type(data) is dict:
            data = LightConfig(data)
        if type(data) in (dict, Config, LightConfig):
            for key, value in data.items():
                data[key] = self._walk_populate(value)
            if '__path__' in data or '__class__' in data:
                if '__path__' not in data:
                    logger.error(
                        '#{} missing __path__ key for object import'.format(shortid(self)))
                elif '__class__' not in data:
                    logger.error(
                        '#{} missing __class__ key for object import'.format(shortid(self)))
                else:
                    obj = self.__instantiate_object(data)

                    return obj
        elif type(data) in (list, tuple):
            for i, value in enumerate(data):
                data[i] = self._walk_populate(value)
        return data
    
    def __instantiate_object(self, data):
        classname = data['__class__']
        path = data['__path__']

        args = data.get('__args__', [])
        kwargs = data.get('__kwargs__', {})
        pass_dict = data.get('__dict__', False)
        if pass_dict:
            arg_data = dict(data)
            del arg_data['__class__']
            del arg_data['__path__']
            del arg_data['__dict__']
            if '__kwargs__' in arg_data:
                del arg_data['__kwargs__']
            if '__args__' in arg_data:
                del arg_data['__args__']
            if pass_dict == True:
                args.append(arg_data)
            else:
                kwargs[pass_dict] = arg_data

        logger.debug2(
            '#{} object {} import from {}'.format(shortid(self), classname, path))

        cls_ = self.loader.load_type(path, classname)

        logger.debug2(
            '#{} instantiate {} with parameters {} and {}'.format(shortid(self), classname, args, kwargs))

        obj = cls_(*args, **kwargs)
        return obj


class ConfigStructure(object):
    def __init__(self, filter_=None, parent=None):
        self.parameters = {}
        self._filter = filter_

        self.children = []
        self.parent = parent
        if self.parent:
            self.parent.children.append(self)
    
    def retrieve_parameters(self, top, filename=None):
        logger.debug2(
            'Looking up parameters for {}'.format(filename))
        parameters = {}
        if top or (filename and self.matches(filename)):
            parameters.update(self.parameters)
        for child in self.children:
            parameters.update(child.retrieve_parameters(False, filename=filename))
        return parameters
    
    def filter(self, filename):
        matches = self.find_matches(filename, strict=True)
        if matches:
            return matches[0]
        return ConfigStructure(filename, self)

    def matches(self, filename, strict=False):
        filename = filename.replace('\\', '/')
        if self._filter is None:
            return False
        if strict:
            return filename == self._filter
        return re.match(self._filter.replace('/', r'\/').replace('*', '(.*)'), filename)

    def find_matches(self, filename, strict=False):
        return [child for child in self.children if child.matches(filename, strict=strict)]
    
    def parameter(self, key):
        if key not in self.parameters:
            self.parameters[key] = Parameter()
        return self.parameters[key]


class Parameter(object):
    def __init__(self):
        self._key = None
        self._file = None
    
    def __repr__(self):
        return 'Parameter(k:{}, c:{})'.format(self._key, self._file)

    def import_key(self, key, filename=[]):
        if not isinstance(filename, list):
            filename = [filename]
        self._key = (key, filename)

    def import_file(self, folder):
        if not isinstance(folder, list):
            folder = [folder]
        self._file = folder
