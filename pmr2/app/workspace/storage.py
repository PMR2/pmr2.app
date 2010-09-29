import zope.interface

from pmr2.app.workspace.interfaces import IStorage
from pmr2.app.workspace.interfaces import IStorageUtility


class BaseStorage(object):
    """\
    Basic storage type
    """

    zope.interface.implements(IStorage)

    def __init__(self, root, rev=None):
        """\
        Instantiate storage at root at the revision.
        """


class StorageUtility(object):
    """\
    Basic storage utility.

    Reason why we have a utility instead of a straight-up adapter to a
    Storage object is two-folds.

    Usage in vocabularies with a context.  The given context may be of a
    type that cannot be adapted into a Storage object.  As the storage
    types are provided globally, it makes more sense to make this a 
    globally available utility.

    Second, this allows the other classes to subclass Storage without
    worrying about including this for cases where independence from the
    Workspace concept is desired.
    """

    zope.interface.implements(IStorageUtility)

    def __call__(self):
        """\
        Converts workspace into a storage object
        """
        raise NotImplementedError
