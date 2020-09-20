from exlab.interface.loader import Loader
from exlab.lab.database import Database
from exlab.lab.counter import Counter
from exlab.modular.module import Module, manage
from exlab.utils.io import shortid


class Experiment(Module):
    def __init__(self, lab, config, database=None, counter=Counter):
        Module.__init__(self, 'Experiment', lab)
        self.lab = lab
        self.config = config

        # Logging
        self.logger.enable_debug2()
        self.logger.info(
            f'#{shortid(self)} Creating a new experiment', tag='EXP')
        self.logger.debug2(
            f'with config {self.config}', tag='EXP')
        if database:
            self.logger.info(
                f'loading database {database}', tag='EXP')
        else:
            database = Database.from_experiment(self)

        self.database = database

        # Init counter
        manage(self).attach_counter(counter())
        self.logger.info(
            f'Starting with counter {self.counter}', tag='EXP')
    
    @property
    def counter(self):
        return self._exlab_manager.counter

    def run(self, callback=None):
        self.logger.info(
            f'#{shortid(self)} Starting experiment', tag='EXP')
        self.config.populate(Loader.instance())
        self._perform(callback=callback)
        self.logger.info(
            f'#{shortid(self)} Experiment finished', tag='EXP')
    
    def _perform(self, callback=None):
        if callback is None:
            self.logger.error(
                f'#{shortid(self)} No behaviour set! Specify a callback function in Lab.run(f) or subclass Experiment and overload _run.', tag='EXP')
            return
        callback(self)
    
    def __repr__(self):
        return f'Experiment {shortid(self)}'
