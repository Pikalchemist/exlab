from exlab.utils.path import ymlbpath
from exlab.utils.structure import get_sub_dict_path, get_dict_path
from exlab.modular.logger import logging

import yaml
import os
import re


class Config(dict):
    def __init__(self, basedir='', structure=None, top=True):
        super(Config, self).__init__()
        self.top = top
        self.structure = structure if structure else ConfigStructure()
        self.parameters = {}

        self.basedir = basedir

    def load_file(self, filename):
        data = self._load_data_from_file(filename)
        self.update(data)
        self._load_parameters(filename)
        print(self)

    def _load_data_from_file(self, filename):
        filename = ymlbpath(self.basedir, filename)
        try:
            with open(filename) as f:
                data = yaml.load(f, Loader=yaml.FullLoader)
            self._walk_dict(data)
            return data
        except Exception as e:
            print(e)
            return {}

    def _walk_dict(self, data):
        if type(data) is dict:
            for key, value in data.items():
                if key == '__import__':
                    data.clear()
                    data.update(self._load_data_from_file(value))
                    break
                else:
                    self._walk_dict(value)
        elif type(data) in (list, tuple):
            for value in data:
                self._walk_dict(value)

    def load_args(self, argv):
        pass

    def _load_parameters(self, filename=None):
        parameters = self.structure.retrieve_parameters(self.top, filename)
        for key, parameter in parameters.items():
            try:
                sdict, skey = get_sub_dict_path(self, key)
                if skey in sdict:
                    if parameter._key:
                        (tkey, tfilename) = parameter._key
                        if tfilename:
                            config = Config(self.basedir, structure=self.structure, top=False)
                            config.load_file(tfilename)
                        else:
                            config = self
                        sdict[skey] = get_dict_path(config, tkey).get(sdict[skey])
                    if parameter._config:
                        config = Config(os.path.join(
                            self.basedir, parameter._config), structure=self.structure, top=False)
                        config.load_file(sdict[skey])
                        sdict[skey] = config
            except KeyError:
                continue


    def populate(self):
        pass


class ConfigStructure(object):
    def __init__(self, filter_=None, parent=None):
        self.parameters = {}
        self._filter = filter_

        self.children = []
        self.parent = parent
        if self.parent:
            self.parent.children.append(self)
    
    def retrieve_parameters(self, top, filename=None):
        parameters = {}
        if top or (filename and self.matches(filename)):
            parameters.update(self.parameters)
        for child in self.children:
            parameters.update(child.retrieve_parameters(False))
        return parameters
    
    def filter(self, filename):
        matches = self.find_matches(filename, strict=True)
        if matches:
            return matches[0]
        return ConfigStructure(filename, self)

    def matches(self, filename, strict=False):
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
        self._object = None

    def key(self, key, filename=None):
        self._key = (key, filename)

    def config(self, folder):
        self._config = folder

    def object(self, obj):
        self._object = obj
