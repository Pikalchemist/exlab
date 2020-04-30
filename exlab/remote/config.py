from exlab.utils.path import ymlbpath
from exlab.utils.structure import get_sub_dict_path, get_dict_path
from exlab.remote.loader import Loader
import exlab.modular.logger as exlogger

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
    def __init__(self, basedir='', structure=None, top=True, relativedir='', topdir='', loader=None):
        super(Config, self).__init__()
        self.top = top
        self.structure = structure if structure else ConfigStructure()
        self.parameters = {}

        self.basedir = basedir
        self.topdir = topdir if topdir else basedir
        self.relativedir = relativedir
    
        self.loader = loader

        logger.debug('#{} config file created, basedir {}'.format(
            id(self), self.basedir))

    def load_file(self, filename):
        logger.debug2('#{} load file {}'.format(id(self), filename))

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
                id(self), filename, e))
            return {}

    def load_args(self, argv):
        pass

    def _load_parameters(self, filename=None):
        parameters = self.structure.retrieve_parameters(self.top, os.path.join(self.relativedir, filename))
        logger.debug2(
            '#{} parameters {}'.format(id(self), parameters))

        for key, parameter in parameters.items():
            try:
                sdict, skey = get_sub_dict_path(self, key)
                if skey in sdict:
                    if parameter._key:
                        (tkey, tfilename) = parameter._key
                        if tfilename:
                            config = Config(self.topdir, structure=self.structure, top=False)
                            config.load_file(tfilename)
                        else:
                            config = self
                        sdict[skey] = get_dict_path(config, tkey).get(sdict[skey])
                    if parameter._config:
                        config = Config(os.path.join(
                            self.basedir, parameter._config),
                            topdir=self.topdir,
                            relativedir=os.path.join(self.relativedir, parameter._config),
                            structure=self.structure, top=False)
                        config.load_file(sdict[skey])
                        sdict[skey] = config
            except KeyError:
                continue

    def populate(self, loader=None):
        loader = loader if loader else self.loader
        if not loader:
            loader = Loader(self.basedir)
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
                    '#{} import from {}'.format(id(self), filename))

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
                        '#{} missing __path__ key for object import'.format(id(self)))
                elif '__class__' not in data:
                    logger.error(
                        '#{} missing __class__ key for object import'.format(id(self)))
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
            '#{} object {} import from {}'.format(id(self), classname, path))

        cls_ = self.loader.load_type(path, classname)

        logger.debug2(
            '#{} instantiate {} with parameters {} and {}'.format(id(self), classname, args, kwargs))

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
        self._config = None
    
    def __repr__(self):
        return 'Parameter(k:{}, c:{})'.format(self._key, self._config)

    def key(self, key, filename=None):
        self._key = (key, filename)

    def config(self, folder):
        self._config = folder
