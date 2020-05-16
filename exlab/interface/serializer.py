'''
    Author: Alexandre Manoury
    Python Version: 3.6
'''

import os
from enum import Enum
import numpy as np
import copy


# def serialize(instance, keys, refkeys=[], exportPathType=False, options={}):
#     dict_ = {}

#     if exportPathType:
#         from exlab.interface.loader import Loader
#         dict_['type'] = instance.__class__.__name__
#         dict_['path'] = os.path.splitext(Loader.instance().classPath(instance))[0]
#     for key in keys:
#         attr = getattr(instance, key)
#         if attr is not None:
#             dict_[key] = attr
#     for key in refkeys:
#         attr = getattr(instance, key)
#         if attr is not None:
#             dict_[key] = attr.primary_key()

#     return Serializer.serialize_data(dict_, options=options)


class Serializer(object):
    GID_ALREADY_DEFINED = 'Global Identifier "{}" is already associated with {} while trying to be redefined by {}'
    GID_MISSING = 'The object "{}" has been serialized twice, please add a Global Identifier .gid() to it to avoid ' + \
                  'Circular dependencies.'
    SERIALIZER = 'serializer'

    def __init__(self, root=None, options=None):
        # self.objects = {}
        self.root = root if root else self
        self.ids = {}

        self._data = {}

        self.options = {}
        if self.root is not self:
            self.options = copy.copy(self.root.options)
        if options:
            self.options.update(options)

    def add(self, obj, id_=None):
        id_ = id_ if id_ else id(obj)
        self.root.ids[id_] = obj

    def get(self, id_):
        return self.root.ids.get(id_)
    
    def clone(self, options=None):
        return self.__class__(self, options)
    
    @property
    def data(self):
        return self.root._data

    # @staticmethod
    # def make_gid(instance, *args):
    #     return '{}::({})'.format(instance.__class__.__name__, '|'.join(map(str, args)))

    # @staticmethod
    # def make_gid_from_cid(instance, cid):
    #     return '{}::#({})'.format(instance.__class__.__name__, cid)

    def serialize(self, instance, keys=[], refkeys=[], export_path_type=True):
        dict_ = {}

        if export_path_type:
            from exlab.interface.loader import Loader
            dict_['__class__'] = instance.__class__.__name__
            dict_['__path__'] = Loader.instance().class_path(instance)
            dict_['__dict__'] = True

        dict_['__id__'] = id(instance)

        for keylist, onlyid in ((keys, False), (refkeys, True)):
            for key in keylist:
                attr = getattr(instance, key)
                if callable(attr):
                    attr = attr()
                if attr is not None:
                    dict_[key.lstrip('_')] = {'__id__': '@' + str(id(attr))} if onlyid else attr

        return self.serialize_data(dict_)

    def serialize_key(self, x):
        t = type(x)
        if t in (int, str, float, bool):
            return x

        return '@' + id(x)

    def serialize_data(self, x):
        t = type(x)

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
            return x.serialize(serializer=self)

        return x

    def deserialize(self, dict_, *args, context=[], **kwargs):
        if type(dict_) in (list, tuple, set):
            return [self.deserialize(x, *args, context=context, **kwargs) for x in dict_]
        if not type(dict_) in (dict,):
            return dict_

        from exlab.interface.loader import Loader
        self = Loader.instance().load(dict_['path'], dict_['type'])
        return self.deserialize(dict_, *args, context=context, **kwargs)


def getReference(caption, type_='', id_data=''):
    return "[[{}||{}||{}]]".format(caption, type_, id_data)


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
        pass

    def serialize(self, serializer=None):
        serializer = serializer if serializer is not None else Serializer()
        if serializer.get(id(self)):
            return {'__id__': '@' + str(id(self))}
        serializer.add(self)

        dict_ = self._serialize(serializer)

        return dict_

    @classmethod
    def deserialize(cls, dict_, serializer=None):
        serializer = serializer if serializer is not None else Serializer()

        id_ = dict_.get('__id__')
        if id_ and id_[0] == '@':
            id_ = id_[1:]
            if serializer.get(id_):
                return serializer.get(id_)

        obj = cls._deserialize(dict_, serializer)

        serializer.add(obj, id_=id_)
        return obj
