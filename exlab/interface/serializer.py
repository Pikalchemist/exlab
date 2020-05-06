'''
    Author: Alexandre Manoury
    Python Version: 3.6
'''

import os
from enum import Enum
import numpy as np


def serialize(instance, keys, refkeys=[], exportPathType=False, options={}):
    dict_ = {}

    if exportPathType:
        from exlab.interface.loader import Loader
        dict_['type'] = instance.__class__.__name__
        dict_['path'] = os.path.splitext(Loader.instance().classPath(instance))[0]
    for key in keys:
        attr = getattr(instance, key)
        if attr is not None:
            dict_[key] = attr
    for key in refkeys:
        attr = getattr(instance, key)
        if attr is not None:
            dict_[key] = attr.primary_key()

    return Serializer.serialize_data(dict_, options=options)


class Serializer(object):
    GID_ALREADY_DEFINED = 'Global Identifier "{}" is already associated with {} while trying to be redefined by {}'
    GID_MISSING = 'The object "{}" has been serialized twice, please add a Global Identifier .gid() to it to avoid ' + \
                  'Circular dependencies.'
    SERIALIZER = 'serializer'

    def __init__(self):
        self.objects = {}
        self.ids = {}

    def add(self, obj, gid=None):
        if not gid and hasattr(obj, 'gid'):
            gid = obj.gid()
        if gid:
            if self.get(gid):
                raise Exception(self.GID_ALREADY_DEFINED.format(gid, self.get(gid), obj))
            self.objects[gid] = obj

        # check ids
        if self.ids.get(id(obj)):
            raise Exception(self.GID_MISSING.format(obj))
        self.ids[id(obj)] = obj

    def get(self, gid):
        return self.objects.get(gid)

    @classmethod
    def create_options(cls):
        options = {
            cls.SERIALIZER: cls()
        }
        return options

    @classmethod
    def serializer(cls, options):
        return options.get(cls.SERIALIZER)

    @staticmethod
    def make_gid(instance, *args):
        return '{}::({})'.format(instance.__class__.__name__, '|'.join(map(str, args)))

    @staticmethod
    def make_gid_from_cid(instance, cid):
        return '{}::#({})'.format(instance.__class__.__name__, cid)

    @classmethod
    def serialize(cls, instance, keys=[], refkeys=[], exportPathType=True, options={}):
        dict_ = {}

        if exportPathType:
            from exlab.interface.loader import Loader
            dict_['type'] = instance.__class__.__name__
            dict_['path'] = os.path.splitext(Loader.instance().classPath(instance))[0]

        keys += ['cid', 'gid']
        for key in keys:
            attr = getattr(instance, key)
            if callable(attr):
                attr = attr()
            if attr is not None:
                dict_[key.lstrip('_')] = attr

        for key in refkeys:
            attr = getattr(instance, key)
            if attr is not None:
                dict_[key] = attr.primary_key()

        return cls.serialize_data(dict_, options=options)

    @classmethod
    def serialize_key(cls, x, options={}):
        if hasattr(x, 'gid'):
            gid = x.gid()
            if gid:
                return gid

        return str(x)

    @classmethod
    def serialize_data(cls, x, options={}):
        t = type(x)

        if t in (int, str, float, bool):
            return x
        if t in (list, tuple, set):
            return t([cls.serialize_data(v, options=options) for v in x])
        if t in (dict,):
            return {cls.serialize_key(k, options=options): cls.serialize_data(v, options=options) for k, v in x.items()}
        if isinstance(x, Enum):
            return x.value
        if type(x).__module__ == np.__name__:
            return x.tolist()
        if hasattr(x, 'serialize'):
            return x.serialize(options=options)

        return x

    @classmethod
    def deserialize(cls, dict_, *args, options={}, context=[], **kwargs):
        if type(dict_) in (list, tuple, set):
            return [cls.deserialize(x, *args, options=options, context=context, **kwargs) for x in dict_]
        if not type(dict_) in (dict,):
            return dict_

        from exlab.interface.loader import Loader
        cls = Loader.instance().loadType(dict_['path'], dict_['type'])
        return cls.deserialize(dict_, *args, options=options, context=context, **kwargs)


def getReference(caption, type_='', id_data=''):
    return "[[{}||{}||{}]]".format(caption, type_, id_data)


class Serializable(object):
    def cid(self):
        return None

    def gid(self):
        if self.cid():
            return Serializer.make_gid_from_cid(self, self.cid())
        return None

    def _serialize(self, options):
        pass

    @classmethod
    def _deserialize(cls, dict_, options, obj=None):
        pass

    def serialize(self, options=None):
        options = options if options else Serializer.create_options()
        serializer = Serializer.serializer(options)
        if self.gid() and serializer.get(self.gid()):
            return {'gid': self.gid(), '--import': 'gid-only'}
        # print('Serial {}'.format(self.__class__))
        serializer.add(self)

        dict_ = self._serialize(options)

        return dict_

    @classmethod
    def deserialize(cls, dict_, *args, options=None, context=[], **kwargs):
        options = options if options else Serializer.create_options()
        serializer = Serializer.serializer(options)

        for entity in context:
            entity.serialize(options=options)

        gid = dict_.get('gid')
        if gid and serializer.get(gid):
            return serializer.get(gid)

        obj = cls._deserialize(dict_, *args, options=options, **kwargs)

        serializer.add(obj, gid=gid)
        return obj
