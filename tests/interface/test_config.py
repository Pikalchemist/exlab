import unittest
from pathlib import Path

from exlab.interface.config import Config, ConfigStructure
from exlab.interface.loader import Loader, register_sourcepath


register_sourcepath(Path(__file__).parent / 'data')


class TestLoader(unittest.TestCase):
    def test_simple(self):
        config = Config(Path(__file__).parent / 'data')
        
        self.assertEqual(config, {})
        self.assertEqual(config.data, {})
        self.assertEqual(config.basedir, Path(__file__).parent / 'data')

        config.load_file('config')
        # print(config)

        truth = {
            'name': 'Hello',
            'learner': 'test/learner1',
            'infos': {'dataset': 'ds1'},
            'names': {'Hello': True}
        }
        self.assertEqual(config, truth)
        self.assertEqual(config.data, truth)

        # configs.load_args(sys.argv[1:])

        # for config in configs.grid():
        #     self.experiments.append(self.experiment_class(
        #         self, config, counter=counter))
    
    def test_imports(self):
        config = Config(Path(__file__).parent / 'data')
        config.load_file('data')

        truth = {
            'datasets': {
                'ds1': {'name': 'Dataset 1', 'path': 'ds1'},
                'ds2': {'name': 'Dataset 2', 'path': 'ds2'}
            }
        }
        self.assertEqual(config, truth)
        self.assertEqual(config.data, truth)
    
    def test_import_key(self):
        structure = ConfigStructure()
        structure.parameter('infos.dataset').import_key('datasets', 'data')

        config = Config(Path(__file__).parent / 'data', structure=structure)
        config.load_file('config')

        truth = {
            'name': 'Hello',
            'learner': 'test/learner1',
            'infos': {'dataset': {'name': 'Dataset 1', 'path': 'ds1'}},
            'names': {'Hello': True}
        }
        self.assertEqual(config, truth)
        self.assertEqual(config.data, truth)

        # Root
        structure = ConfigStructure()
        structure.parameter('infos.dataset').import_key('', 'datasets')

        config = Config(Path(__file__).parent / 'data', structure=structure)
        config.load_file('config')

        self.assertEqual(config, truth)
        self.assertEqual(config.data, truth)
    
    def test_import_file(self):
        structure = ConfigStructure()
        structure.parameter('learner').import_file(['learners', 'learners2'])

        config = Config(Path(__file__).parent / 'data', structure=structure)
        config.load_file('config')

        truth = {
            'name': 'Learner 1'
        }
        self.assertEqual(dict(config['learner'], **truth), config['learner'])
        self.assertEqual(dict(config['learner'].data, **truth), config['learner'].data)

        # Learner 2
        config = Config(Path(__file__).parent / 'data', structure=structure)
        config.load_file('config2')

        truth = {
            'name': 'Learner 2'
        }
        self.assertEqual(dict(config['learner'], **truth), config['learner'])
        self.assertEqual(
            dict(config['learner'].data, **truth), config['learner'].data)
    
    def test_populate(self):
        config = Config(Path(__file__).parent / 'data')
        config.load_file('learners/test/learner1')

        truth = {
            '__path__': 'learner.py',
            '__class__': 'SerialLearner',
            '__dict__': True,
            'name': 'Learner 1',
            'obj': {
                '__path__': 'learner.py',
                '__class__': 'Mod',
                '__args__': [1, 2, 3],
                '__dict__': True,
                'test': 'Hello'
            },
            'dataset': 'ds2'
        }
        self.assertEqual(dict(config, **truth), config)
        self.assertEqual(dict(config.data, **truth), config.data)

        obj = config.populate()['object']
        self.assertEqual(obj.__class__.__name__, 'SerialLearner')
        self.assertEqual(obj.args[0], 'Learner 1')
        self.assertEqual(obj.args[1].__class__.__name__, 'Mod')

        self.assertEqual(dict(config.data, **truth), config.data)
        self.assertIsNotNone(config.serializer)
        self.assertEqual(config.serializer.data['learner'], obj)
        self.assertEqual(config.serializer.options, {})


if __name__ == '__main__':
    unittest.main()
