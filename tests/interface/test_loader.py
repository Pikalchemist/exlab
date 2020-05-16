import unittest
from pathlib import Path

from exlab.interface.loader import Loader, register_sourcepath


register_sourcepath(Path(__file__).parent / 'data')


class TestLoader(unittest.TestCase):
    def test_singleton(self):
        l = Loader.instance()
        l2 = Loader.instance()

        self.assertEqual(l, l2)

    def test_load(self):
        learner = Loader.instance().load('learner', 'Learner')
        self.assertEqual(learner.__name__, 'Learner')

        learner = Loader.instance().instantiate('learner', 'Learner')
        self.assertEqual(learner.__class__.__name__, 'Learner')
    
    def test_load_deserialize(self):
        learner = Loader.instance().load('learner', 'SerialLearner')
        self.assertEqual(learner.__name__, 'SerialLearner')

        learner = Loader.instance().instantiate('learner', 'SerialLearner')
        self.assertEqual(learner.__class__.__name__, 'SerialLearner')

    def test_save(self):
        from learner import Learner
        learner = Learner()
        class_path = Loader.instance().class_path(learner)

        self.assertEqual(class_path, 'learner')


if __name__ == '__main__':
    unittest.main()
