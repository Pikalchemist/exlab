from exlab.interface.loader import Loader
from exlab.lab.database import Database
from exlab.lab.counter import Counter
from exlab.modular.module import Module
from exlab.utils.io import shortid


class Experiment(Module):
    def __init__(self, lab, config, database=None, counter=Counter):
        Module.__init__(self, 'Experiment', lab)
        self.lab = lab
        self.config = config

        # Logging
        self._module.logger.enable_debug2()
        self._module.logger.info(
            '#{} Creating a new experiment'.format(shortid(self)), tag='EXP')
        self._module.logger.debug2(
            'with config {}'.format(self.config), tag='EXP')
        if database:
            self._module.logger.info(
                'loading database {}'.format(database), tag='EXP')
        else:
            database = Database.from_experiment(self)

        self.database = database

        # Init counter
        self._module.attach_counter(counter())
        self._module.logger.info(
            'Starting with counter {}'.format(self.counter), tag='EXP')
    
    @property
    def counter(self):
        return self._module.counter

    def run(self, callback=None):
        self._module.logger.info(
            '#{} Starting experiment'.format(shortid(self)), tag='EXP')
        self.config.populate(Loader.instance())
        self._perform(callback=callback)
        self._module.logger.info(
            '#{} Experiment finished'.format(shortid(self)), tag='EXP')
    
    def _perform(self, callback=None):
        if callback is None:
            self._module.logger.error(
                '#{} No behaviour set! Specify a callback function in Lab.run(f) or subclass Experiment and overload _run.'.format(shortid(self)), tag='EXP')
            return
        callback(self)
    
    def __repr__(self):
        return 'Experiment {}'.format(shortid(self))
