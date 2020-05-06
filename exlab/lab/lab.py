from exlab.interface.config import Config, ConfigStructure
from exlab.interface.loader import Loader
from exlab.modular.modular import Modular

import sys


class Lab(Modular):
    def __init__(self, configdir='.', defaults=None, sourcedir=None, help=''):
        Modular.__init__(self, 'Lab')
        self.help = help

        if type(configdir) is not list:
            configdir = [configdir]
        if sourcedir and type(sourcedir) is not list:
            sourcedir = [sourcedir]
        self.configdir = configdir
        Loader.instance(sourcedir if sourcedir else self.configdir)

        self.defaults = defaults
        self.experiments = []
        self.config_structure = ConfigStructure()
    
    def parameter(self, key):
        return self.config_structure.parameter(key)

    def filter(self, name):
        return self.config_structure.filter(name)
    
    def load(self, filename=None):
        config = Config(self.configdir[0], structure=self.config_structure)
        if self.defaults:
            config.load_file(self.defaults)
        if filename:
            config.load_file(filename)
        config.load_args(sys.argv[1:])
        config.populate(Loader.instance())

        print(config)
        print(config.data)
