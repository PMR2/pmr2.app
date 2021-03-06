import zope.interface
import zope.component
from zope.location import Location, locate

from pmr2.app.factory.interfaces import INamedUtilBase


def name_utility(obj, event):
    """\
    Writes the name of the utility when it is registered.  Used by
    subscriber.
    """

    locate(obj, None, event.object.name)

def named_factory(klass):
    """\
    Named Factory maker
    """

    class _factory(Location):
        zope.interface.implements(INamedUtilBase)
        def __init__(self):
            self.title = klass.title
            self.label = klass.label
            self.description = klass.description
        def __call__(self, *a, **kw):
            # returns an instantiated factory with a context
            factory = klass(*a, **kw)
            factory.__name__ = self.__name__
            return factory
    # create/return instance of the factory that instantiates the 
    # classes below.
    return _factory()


class NamedUtilBase(Location):
    """\
    Class that allows a utility to be named.
    """

    zope.interface.implements(INamedUtilBase)
    title = None
    label = None
    description = None

    def __init__(self, context):
        self.context = context

    @property
    def name(self):
        return self.__name__
