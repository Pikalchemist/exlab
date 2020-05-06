from exlab.interface.loader import Loader
from exlab.utils.io import shortid
from exlab.modular.modular import Modular


class Experiment(Modular):
    def __init__(self, lab, config, database=None):
        Modular.__init__(self, 'Experiment', lab)
        self.lab = lab
        self.config = config
        self.database = database

        self.module.logger.enable_debug2()
        self.module.logger.info(
            '#{} Creating a new experiment'.format(shortid(self)), tag='EXP')
        self.module.logger.debug2(
            'with config {}'.format(self.config), tag='EXP')

    def run(self):
        self.module.logger.info(
            '#{} Starting experiment'.format(shortid(self)), tag='EXP')
        self.config.populate(Loader.instance())
        self.module.logger.info(
            '#{} Experiment finished'.format(shortid(self)), tag='EXP')
    
    def __repr__(self):
        return 'Experiment {}'.format(id(self))
