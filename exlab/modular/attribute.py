

# class AttributeWrapper(object):
#     def __init__(self, baseObject):
#         self.__class__ = type(baseObject.__class__.__name__,
#                               (self.__class__, baseObject.__class__),
#                               {})
#         # self.__dict__ = baseObject.__dict__

#         self._tracking = True


class Attribute(object):
    def __init__(self, name, is_class_attribute):
        self.name = name
        self.is_class_attribute = is_class_attribute

    def make_accessible(self, editable=False, index=None):
        self.editable = editable
        self.index = index
    
    def set_hyperparameter(self, help_=None, range_=None, how_to_choose=None):
        self.help = help_
        self.range = range_
        self.how_to_choose = how_to_choose
        

    def __repr__(self):
        return f'Attribute.{self.name}'


# def attribute(attr):
#     print(id(attr))


# def track():
#     return None


# class Test(object):
#     def __init__(self):
#         self.a: track() = Attribute('test')
#         print(id(self.a))
#         attribute(self.a)
#         print(self.__init__.__annotations__)

# test = Test()

# a = 15
# b = AttributeWrapper(a)
# print(a)
# print(b)


# wrap = Wrapper(test)
# print(type(wrap))
# print(type(wrap.a))
# print(wrap._tracking)


# class Wrapper(object):
#     __ignore = "class mro new init setattr getattr getattribute"
#     __methods = "repr"

#     def __init__(self, obj):
#         self._obj = obj

#         def test(self):
#             return 'a'

#         setattr(self, '__repr__ ', test)

#     def __getattr__(self, name):
#         return getattr(self._obj, name)
    
#     def __repr__(self):
#         return self._obj.__repr__()
    
#     def __add__(self, o):
#         return self._obj.__add__(o)
    
#     # class __metaclass__(type):
#     #     def __init__(cls, name, bases, dct):

#     #         def make_proxy(name):
#     #             def proxy(self, *args):
#     #                 return getattr(self._obj, name)
#     #             return proxy

#     #         type.__init__(cls, name, bases, dct)
#     #         for name in cls.__methods:
#     #             if name.startswith("__"):
#     #                 if name not in dct:
#     #                     setattr(cls, name, property(make_proxy(name)))


# w = Wrapper(2)
# w2 = Wrapper(2)
# print(repr(w))
# print(w + 2)
