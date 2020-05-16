from exlab.interface.config import Config, ConfigStructure
from exlab.interface.loader import Loader
from exlab.modular.module import Module
from exlab.lab.experiment import Experiment

import sys
import os


class Lab(Module):
    def __init__(self, configdir='.', defaults=None, sourcedir=None, databasedir=None, help=''):
        Module.__init__(self, 'Lab')
        self.help = help

        if type(configdir) is not list:
            configdir = [configdir]
        if not sourcedir:
            sourcedir = configdir
        if sourcedir and type(sourcedir) is not list:
            sourcedir = [sourcedir]
        self.configdir = configdir

        databasedir = databasedir if databasedir else os.path.join(
            self.configdir[0], 'databases')

        Loader.instance().add_source(sourcedir)
        Loader.instance().set_databasedir(databasedir)

        self.defaults = defaults
        self.experiments = []
        self.config_structure = ConfigStructure()

        self.experiment_class = Experiment
    
    def parameter(self, key):
        return self.config_structure.parameter(key)

    def filter(self, name):
        return self.config_structure.filter(name)
    
    def run(self, callback=None, thread=False):
        if not self.experiments:
            raise Exception('No experiment exist in this lab, please use Lab.load() first')
        for experiment in self.experiments:
            experiment.run(callback=callback)
    
    def set_experiment_class(self, experiment_class):
        self.experiment_class = experiment_class
    
    def load(self, filename=None, experiment_class=None, counter=None):
        if experiment_class:
            self.set_experiment_class(experiment_class)

        configs = Config(self.configdir[0], structure=self.config_structure)
        if self.defaults:
            configs.load_file(self.defaults)
        if filename:
            configs.load_file(filename)
        configs.load_args(sys.argv[1:])

        for config in configs.grid():
            self.experiments.append(self.experiment_class(
                self, config, counter=counter))

