import unittest
from pathlib import Path

from exlab.interface.serializer import Serializable, Serializer
from exlab.interface.loader import register_sourcepath


# Register tests/ as top source path
register_sourcepath(Path(__file__).parent.parent)


class TestSerializer(unittest.TestCase):
    def test_simple_serialize(self):
        person = Person('Albert', 30)
        dict_ = person.serialize()
        # print(dict_)

        truth = {
            '__class__': 'Person',
            '__path__': 'interface.test_serializer',
            '__dict__': True,
            '__id__': id(person),
            'name': 'Albert',
            'age': 20,
            'alive': True,
            'children': [],
            'last_birthdays': [18, 19, 20]
        }
        self.assertTrue(dict(dict_, **truth), dict_)

    def test_simple_changes(self):
        person = Person('Albert', 30)
        person.add_child(Person('Mateo', 12))
        dict_ = person.serialize()
        # print(dict_)

        truth = [{
            '__class__': 'Person',
            '__path__': 'interface.test_serializer',
            '__dict__': True,
            '__id__': id(person.children[0]),
            'name': 'Mateo',
            'age': 12,
            'alive': True,
            'children': [],
            'last_birthdays': [10, 11, 12]
            }]
        self.assertListEqual(dict_['children'], truth)
    
    def test_multiple_references(self):
        person = Person('Albert', 30)
        child = Person('Mateo', 12)
        person.add_child(child)
        person.add_child(child)
        dict_ = person.serialize()
        # print(dict_)

        truth = [{
            '__class__': 'Person',
            '__path__': 'interface.test_serializer',
            '__dict__': True,
            '__id__': id(person.children[0]),
            'name': 'Mateo',
            'age': 12,
            'alive': True,
            'children': [],
            'last_birthdays': [10, 11, 12]
        }, {
            '__id__': '@' + str(id(person.children[0]))
        }]
        self.assertListEqual(dict_['children'], truth)
    
    def test_circular_dependencies(self):
        person = Person('Albert', 30)
        person.add_child(Person('Mateo', 12))
        person.add_child(Person('Tim', 12, person))
        dict_ = person.serialize()
        # print(dict_)

        truth = {
            '__id__': '@' + str(id(person))
        }
        self.assertTrue(dict(dict_['children'][1]['guardian'], **truth), dict_['children'][1]['guardian'])
    
    def test_deserialize(self):
        pass


class Person(Serializable):
    def __init__(self, name, age, guardian=None):
        self.name = name
        self.age = age
        self.guardian = guardian

        self.alive = True
        self.last_birthdays = [age - 2, age -1, age]
        self.children = []
    
    def _serialize(self, serializer: Serializer):
        return serializer.serialize(self, ['name', 'age', 'alive', 'children', 'last_birthdays'], ['guardian'])
    
    def add_child(self, child):
        self.children.append(child)


if __name__ == '__main__':
    unittest.main()
