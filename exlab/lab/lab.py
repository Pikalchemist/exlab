from exlab.interface.config import Config, ConfigStructure
from exlab.modular.modular import Modular

import sys


class Lab(Modular):
    def __init__(self, basedir='.', defaults=None, help=''):
        Modular.__init__(self, 'Lab')
        self.help = help
        self.basedir = basedir
        self.defaults = defaults
        self.experiments = []
        self.config_structure = ConfigStructure()
    
    def parameter(self, key):
        return self.config_structure.parameter(key)

    def filter(self, name):
        return self.config_structure.filter(name)
    
    def load(self):
        config = Config(self.basedir, structure=self.config_structure)
        if self.defaults:
            config.load_file(self.defaults)
        config.load_args(sys.argv[1:])
        config.populate()
        print(config)
        print(config.data)
