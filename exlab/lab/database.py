from exlab.utils import io

import exlab.modular.logger as exlogger

from pathlib import Path
import datetime
import time
import os
import yaml


logger = exlogger.ProxyLogger(tag='LOAD')
# logger.displayDebug2()


class Database(object):
    FILENAME =  'database.yml'
    COUNTER = '%count'
    SAVED_ATTRIBUTES = ('date', 'timestamp', 'commit_hashes', 'version')
    VERSION = 1

    fileformat = '{environment}/{name}/{%count}'
    databasedir = Path('c:\\data\\projects\\phd\\dino\\databases') # To None
    escape_spaces = '-'

    def __init__(self, path, config, data):
        if isinstance(path, str):
            dbdir = str(self.databasedir.absolute())
            if path.startswith(dbdir):
                path = path[len(dbdir):]
            path = Path(path)
        self.path = path
        self.config = config
        self.data = data

        self.date = str(datetime.datetime.now())
        self.timestamp = time.time()
        self.commit_hashes = io.get_git_hashes()
        self.version = self.VERSION

    def __repr__(self):
        return f'Database {self.path}'

    def set_fromdict(self, dict_):
        for attribute in self.SAVED_ATTRIBUTES:
            setattr(self, attribute, dict_.get(attribute))

    def save(self):
        self.path.mkdir(parents=True, exist_ok=True)
        saved = {'config': self.config,
                 'saved': self.data}
        for attribute in self.SAVED_ATTRIBUTES:
            saved[attribute] = getattr(self, attribute)

        with open(self.path / self.FILENAME, 'w') as f:
            yaml.dump(saved, f)
    
    def load(self):
        pass
    
    @classmethod
    def set_databasedir(cls, databasedir):
        cls.databasedir = Path(databasedir)
        cls.databasedir.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def create_filepath(cls, config):
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
        dict_.update(config)

        templater = io.Templater(dict_)

        paths = [templater.render(folder) for folder in paths]
        if cls.escape_spaces:
            paths = [p.replace(' ', cls.escape_spaces) for p in paths]
        path = Path.joinpath(cls.databasedir, *paths)

        fullpath = None
        while not fullpath or fullpath.exists():
            if fullpath:
                if cls.COUNTER not in filename:
                    filename += f'_{cls.COUNTER}'
                else:
                    dict_[cls.COUNTER] += 1
            file_ = templater.render(filename)
            if cls.escape_spaces:
                file_ = file_.replace(' ', cls.escape_spaces)
            fullpath = path / file_
        return fullpath
    
    @classmethod
    def from_data(cls, config, data={}):
        folder = cls.create_filepath(config)
        logger.info(f'Create database at {folder}')
        db = Database(folder, config, data)
        return db

    @classmethod
    def from_experiment(cls, experiment, data={}):
        return cls.from_data(experiment.config.data, data)
    
    @classmethod
    def list_databases(cls):
        return cls._list_databases(cls.databasedir)

    @classmethod
    def _list_databases(cls, folder):
        databases = []
        folder = Path(folder)
        for f in folder.iterdir():
            fn = folder / f / cls.FILENAME
            db = cls.from_file(fn)
            if db:
                databases.append(db)
            else:
                databases += cls._list_databases(folder / f)
        return databases
    
    @classmethod
    def from_file(cls, folder):
        dbfile = Path(folder) / cls.FILENAME

        if not dbfile.exists():
            return None
        try:
            with open(dbfile) as f:
                data = yaml.load(f, Loader=yaml.FullLoader)
        except Exception as e:
            logger.warning(
                f'Cannot load data from {dbfile}: {e}')
            return None

        db = Database(folder, data.get('config', {}), data.get('saved', {}))
        db.set_fromdict(data)
        return db
