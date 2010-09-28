import zope.interface

from pmr2.app.workspace.interfaces import IStorage
from pmr2.app.workspace.interfaces import IStorageUtility


class Storage(object):
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
    Basic storage utility type
    """

    zope.interface.implements(IStorageUtility)

    def __call__(self):
        """\
        Converts workspace into a storage object
        """
