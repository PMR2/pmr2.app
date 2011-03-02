import zope.interface
import zope.component
from zope.location import Location, locate
from zope.schema.interfaces import IVocabularyFactory

from pmr2.app.interfaces import *


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
        def __call__(self, context):
            # returns an instantiated factory with a context
            factory = klass(context)
            factory.__name__ = self.__name__
            return factory
    # create/return instance of the factory that instantiates the 
    # classes below.
    return _factory()

def vocab_factory(vocab):
    def _vocab_factory(context):
        return vocab(context)
    zope.interface.alsoProvides(_vocab_factory, IVocabularyFactory)
    return _vocab_factory


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
