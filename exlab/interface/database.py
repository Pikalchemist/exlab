import exlab.modular.logger as exlogger
from exlab.utils import io


import datetime
import time
import os
import yaml


logger = exlogger.getLogger('database', tag='DB')
logger.enable_debug2()


class Database(object):
    FILENAME =  'database.yml'
    COUNTER = '%count'

    fileformat = '{name}/{%count}'
    databasedir = None
    escape_spaces = '-'

    def __init__(self, path, config):
        if path.startswith(self.databasedir):
            path = path[len(self.databasedir):]
        self.path = path
        self.config = config

        self.date = str(datetime.datetime.now())
        self.timestamp = time.time()
        self.commit_hashes = io.get_git_hashes()
    
    def __repr__(self):
        return 'Database {}'.format(self.path)
    
    def set_fromdict(self, dict_):
        for attribute in ('date', 'timestamp', 'commit_hashes'):
            setattr(self, attribute, dict_.get(attribute))
    
    @classmethod
    def from_file(cls, folder):
        dbfile = os.path.join(folder, cls.FILENAME)

        if not os.path.exists(dbfile):
            return None
        try:
            with open(dbfile) as f:
                data = yaml.load(f, Loader=yaml.FullLoader)
        except Exception as e:
            logger.warning('Cannot load data from {}: {}'.format(dbfile, e))
            return None

        db = Database(folder, data.get('config'))
        db.set_fromdict(data)
        return db
    
    @classmethod
    def create_filepath(cls, experiment):
        f = cls.fileformat.split('/')
        paths = f[:-1]
        filename = f[-1]

        dict_ = {
            '%datetime':    datetime.datetime.now().strftime('%Y-%m-%d'),
            '%date':        str(datetime.date.today()),
            '%time':        datetime.datetime.now().strftime('%H-%M-%S'),
            cls.COUNTER:    0
        }
        for char in ('Y', 'm', 'd', 'H', 'M', 'S'):
            key = '%' + char
            dict_[key] = datetime.datetime.now().strftime(key)
        dict_.update(experiment.config.data)

        templater = io.Templater(dict_)

        paths = [templater.render(folder) for folder in paths]
        path = os.path.join(cls.databasedir, *paths)
        if cls.escape_spaces:
            path = path.replace(' ', cls.escape_spaces)

        fullpath = None
        while not fullpath or os.path.exists(fullpath):
            if fullpath:
                if cls.COUNTER not in filename:
                    filename += '_{}'.format(cls.COUNTER)
                else:
                    dict_[cls.COUNTER] += 1
            file_ = templater.render(filename)
            if cls.escape_spaces:
                file_ = file_.replace(' ', cls.escape_spaces)
            fullpath = os.path.join(path, file_)
        return fullpath
    
    @classmethod
    def from_experiment(cls, experiment):
        folder = cls.create_filepath(experiment)
        logger.info('Create database at {}'.format(folder))
        db = Database(folder, experiment.config.data)
        return db
