import zope.interface

from pmr2.app.workspace.interfaces import IStorage
from pmr2.app.workspace.interfaces import IStorageUtility


class BaseStorage(object):
    """\
    Basic storage type
    """

    zope.interface.implements(IStorage)


class StorageUtility(object):
    """\
    Basic storage utility.

    Reason why we have a utility instead of a straight-up adapter to a
    Storage object is two-folds.

    Usage in vocabularies with a context.  The given context may be of a
    type that cannot be adapted into a Storage object.  As the storage
    types are provided globally, it makes more sense to make this a 
    globally available utility.  While the subclass of BaseStorage can
    be used instead, this serves as a more lightweight utility rather
    than registering the implementation of the whole storage class.

    Second, this allows the other classes to subclass Storage without
    worrying about including this for cases where independence from the
    Workspace concept is desired.

    Third, initialization for the base storage class is now independent
    of implementation of the utility.
    """

    zope.interface.implements(IStorageUtility)

    def __call__(self, workspace):
        """\
        Converts workspace into a storage object.
        """
        raise NotImplementedError


class BaseStorageAdapter(object):
    """\
    We do need a quick way to adapt any object into its source storage
    mechanism, as not all objects contain reference (name) to its
    storage backend.
    """
