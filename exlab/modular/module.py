from exlab.modular.logger import ProxyLogger
from exlab.modular.node import NodeWithChildren
from exlab.modular.syncable import Syncable, manage
from exlab.interface.serializer import Serializable


class Module(Syncable, Serializable):
    def __init__(self, name='', parent=None):
        self._exlab_manager = Module.Modular(self, name, parent)
        # self._sync = self._module

    @property
    def logger(self):
        return self._exlab_manager.logger

    class Modular(Syncable.Sync, NodeWithChildren):
        def __init__(self, host, name: str = '', parent=None):
            self.logger = None
            Syncable.Sync.__init__(self, host, parent)
            NodeWithChildren.__init__(self, host, parent)

            self.name = name if name else self.host.__class__.__name__

            # Logging
            self.logger = ProxyLogger(self)
            self.logger.info(
                f'Module \'{self.name}\' has been started', tag='Modular')
        
        @property
        def children_modules(self):
            return set(child for child in self.children if isinstance(child, Module.Modular))
        
        def attached(self):
            super()
            if self.logger:
                # self.logger.update()
                self.logger.info(f'Module \'{self.name}\' has been attached to \'{self.parent.name}\'', tag='Modular')

        def detached(self):
            pass
            # if self.logger:
            #     self.logger.update()


# def module(instance):
#     return instance._module


if __name__ == '__main__':
    class Test(Module):
        def __init__(self):
            Module.__init__(self, 'Test')

    t = Test()
    # with t.logger.error('Hello :)', tag='test'):
    #     t.logger.error('Hello :)', tag='test')

