from exlab.interface.loader import Loader
from exlab.interface.database import Database
from exlab.modular.modular import Modular
from exlab.utils.io import shortid


class Experiment(Modular):
    def __init__(self, lab, config, database=None):
        Modular.__init__(self, 'Experiment', lab)
        self.lab = lab
        self.config = config

        self.module.logger.enable_debug2()
        self.module.logger.info(
            '#{} Creating a new experiment'.format(shortid(self)), tag='EXP')
        self.module.logger.debug2(
            'with config {}'.format(self.config), tag='EXP')
        if database:
            self.module.logger.info(
                'loading database {}'.format(database), tag='EXP')
        else:
            database = Database.from_experiment(self)

        self.database = database

    def run(self):
        self.module.logger.info(
            '#{} Starting experiment'.format(shortid(self)), tag='EXP')
        self.config.populate(Loader.instance())
        self.module.logger.info(
            '#{} Experiment finished'.format(shortid(self)), tag='EXP')
    
    def __repr__(self):
        return 'Experiment {}'.format(shortid(self))
