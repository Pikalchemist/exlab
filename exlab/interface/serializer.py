'''
    Author: Alexandre Manoury
    Python Version: 3.6
'''

import os
from enum import Enum
import numpy as np
import copy

from exlab.utils.io import parameter
import exlab.modular.logger as exlogger


logger = exlogger.ProxyLogger(tag='SERIAL')
logger.displayDebug2()

# def serialize(instance, keys, foreigns=[], exportPathType=False, options={}):
#     dict_ = {}

#     if exportPathType:
#         from exlab.interface.loader import Loader
#         dict_['type'] = instance.__class__.__name__
#         dict_['path'] = os.path.splitext(Loader.instance().classPath(instance))[0]
#     for key in keys:
#         attr = getattr(instance, key)
#         if attr is not None:
#             dict_[key] = attr
#     for key in foreigns:
#         attr = getattr(instance, key)
#         if attr is not None:
#             dict_[key] = attr.primary_key()

#     return Serializer.serialize_data(dict_, options=options)


class Serializer(object):
    GID_ALREADY_DEFINED = 'Global Identifier "{}" is already associated with {} while trying to be redefined by {}'
    GID_MISSING = 'The object "{}" has been serialized twice, please add a Global Identifier .gid() to it to avoid ' + \
                  'Circular dependencies.'
    SERIALIZER = 'serializer'

    def __init__(self, root=None, options=None, values=None):
        self.root = root if root else self

        # Shared data
        self.ids = {}

        # Specific data 
        self.finders = {}
        self.values = {}
        self.categoryValues = {}
        self.options = {}

        if self.root is not self:
            self.finders = copy.copy(self.root.finders)
            self.values = copy.copy(self.root.values)
            for category, values in self.root.categoryValues.items():
                self.categoryValues[category] = copy.copy(values)
            self.options = copy.copy(self.root.options)

        if options:
            self.options.update(options)
        if values:
            self.values.update(values)

    def add(self, obj, id_=None):
        id_ = str(id_ if id_ else id(obj))
        if id_[0] == '@':
            id_ = id_[1:]
        self.root.ids[id_] = obj

    def get(self, id_):
        if not id_:
            return
        if isinstance(id_, dict):
            raise Exception(f'ID {id_} is a dictionnary, use Serializer.deserialize instead.')
        id_ = str(id_)
        if id_.startswith('@'):
            id_ = id_[1:]
        if id_ in self.values:
            return self.values[id_]
        s = self.search_finder(id_)
        if s is not None:
            return s
        return self.root.ids.get(id_)
    
    def set(self, key, value, category=None):
        if category:
            if category not in self.categoryValues:
                self.categoryValues[category] = {}
            self.categoryValues[category][key] = value
        else:
            self.values[key] = value
    
    def search_finder(self, id_):
        if ':' not in id_:
            return
        p = id_.find(':')
        namespace = id_[:p]
        if namespace in self.root.finders:
            return self.root.finders[namespace](id_[p + 1:])
        else:
            return self.categoryValues.get(namespace, {}).get(id_[p + 1:])
    
    def clone(self, options=None, values=None):
        return self.__class__(self, options, values)
    
    def attach_finder(self, namespace, method):
        self.root.finders[namespace] = method
    
    # @property
    # def data(self):
    #     return self.root._data

    # @staticmethod
    # def make_gid(instance, *args):
    #     return '{}::({})'.format(instance.__class__.__name__, '|'.join(map(str, args)))

    # @staticmethod
    # def make_gid_from_cid(instance, cid):
    #     return '{}::#({})'.format(instance.__class__.__name__, cid)

    def serialize(self, instance, keys=[], foreigns=[], exportPathType=True):
        dict_ = {}

        if exportPathType:
            from exlab.interface.loader import Loader
            dict_['__class__'] = instance.__class__.__name__
            dict_['__path__'] = Loader.instance().class_path(instance)
            dict_['__dict__'] = True

        dict_['__id__'] = id(instance)

        for keylist, onlyid in ((keys, False), (foreigns, True)):
            for key in keylist:
                attr = getattr(instance, key)
                if callable(attr) and type(attr) is not type:
                    attr = attr()
                if attr is not None:
                    dict_[key.lstrip('_')] = self.serialize_id(attr) if onlyid else attr

        return self.serialize_data(dict_)

    def serialize_id(self, x):
        if hasattr(x, '_sid'):
            return self.serialize_data(x._sid(self))
        return {'__id__': f'@{id(x)}'}

    def serialize_key(self, x):
        t = type(x)
        if t in (int, str, float, bool):
            return x
        id_ = self.serialize_id(x)
        if '__id__' in id_:
            return id_['__id__']

        return f'@{id(x)}'

    def serialize_data(self, x):
        t = type(x)

        if t is type:
            from exlab.interface.loader import Loader
            return {'__class__': x.__name__, '__path__': Loader.instance().class_path(x), '__type__': True}
        if t in (int, str, float, bool):
            return x
        if t in (list, tuple, set):
            return t([self.serialize_data(v) for v in x])
        if t in (dict,):
            return {self.serialize_key(k): self.serialize_data(v) for k, v in x.items()}
        if isinstance(x, Enum):
            return x.value
        if t.__module__ == np.__name__:
            return x.tolist()
        if hasattr(x, 'serialize'):
            return x.serialize(self)

        return x

    def deserialize(self, dict_, context=[], obj=None, default=None):
        if dict_ is None:
            return default
        if type(dict_) in (list, tuple, set):
            return type(dict_)(self.deserialize(x, context=context) for x in dict_)
        if type(dict_) not in (dict,):
            return dict_

        id_ = dict_.get('__id__', '')
        robj = self.get(id_)
        if robj:
            logger.debug(f'D: id {id_} already deserialized: {robj}')
            return robj
        
        if not dict_.get('__dict__'):
            return {self.deserialize(key): self.deserialize(value) for key, value in dict_.items()}

        from exlab.interface.loader import Loader
        cls_ = Loader.instance().load(dict_['__path__'], dict_['__class__'])
        logger.debug(f'D: deserializing: {cls_} with obj {obj}')
        if dict_.get('__type__'):
            return cls_
        else:
            return cls_.deserialize(dict_, self, obj=obj)

    def uid(self, category, id_):
        return {'__id__': f'{category}:{id_}'}
    
    @classmethod
    def check(cls, serialized, key=''):
        errors = []

        t = type(serialized)
        if t in (list, tuple, set):
            for item in serialized:
                errors += cls.check(item, f'{key}[]')
        elif t in (dict,):
            for item in serialized:
                errors += cls.check(serialized[item], f'{key}.{item}')
        elif t not in (int, str, float, bool, bytes):
            errors.append((key, serialized, t))
        return errors


def getReference(caption, type_='', id_data=''):
    return f'[[{caption}||{type_}||{id_data}]]'


class Serializable(object):
    # def _guid(self):
    #     return None

    # def gid(self):
    #     if self.cid():
    #         return Serializer.make_gid_from_cid(self, self.cid())
    #     return None

    def _serialize(self, serializer):
        return {}

    @classmethod
    def _deserialize(cls, dict_, serializer, obj=None):
        return obj

    def _postDeserialize(self, dict_, serializer):
        pass

    def serialize(self, serializer=None):
        serializer = parameter(serializer, Serializer())
        if serializer.get(id(self)):
            return {'__id__': '@' + str(id(self))}
        serializer.add(self)

        dict_ = self._serialize(serializer)

        return dict_

    @classmethod
    def deserialize(cls, dict_, serializer=None, obj=None):
        serializer = parameter(serializer, Serializer())

        id_ = dict_.get('__id__', '')
        robj = serializer.get(id_)
        if robj:
            logger.debug(f'D: id {id_} already deserialized: {robj}')
            return robj

        logger.debug(f'D: deserializing {cls.__name__} (on existing object {obj})')
        obj = cls._deserialize(dict_, serializer, obj=obj)
        logger.debug(f'D: postDeserializing {cls.__name__} on object {obj}')
        obj._postDeserialize(dict_, serializer)

        if id_:
            serializer.add(obj, id_=id_)
        return obj
