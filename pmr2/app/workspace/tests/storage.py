import zope.interface

from pmr2.app.workspace.interfaces import IWorkspace

from pmr2.app.workspace.storage import StorageUtility
from pmr2.app.workspace.storage import BaseStorage


_dummy_storage_data = {

    'test': [
        {
            'file1': 'file1-rev0\nThis is a test.\n',
            'file2': 'file2-rev0\nThis is also a test.\n',
        },
        {
            'file1': 'file1-rev1\nThis test has changed.\n',
            'file2': 'file2-rev1\nThis is also a test.\n',
            'file3': 'A new test file.\n',
        },
    ],

}


class DummyStorageUtility(StorageUtility):
    title = 'Dummy Storage'

    def __call__(self, context):
        return DummyStorage(context)


class DummyStorage(BaseStorage):
    
    def __init__(self, context):
        self.context = context
        self.__id = context.id
        self.checkout(len(self._data()) - 1)

    def _data(self):
        return _dummy_storage_data[self.__id]

    def _changeset(self):
        return self._data()[self.__rev]

    def checkout(self, rev):
        self.__rev = rev

    def files(self):
        result = self._changeset().keys()
        result.sort()
        return result


class DummyWorkspace(object):
    """\
    To avoid the vocab and the rest of Plone Archetypes.
    """

    zope.interface.implements(IWorkspace)

    def __init__(self, id_):
        self.id = id_
        self.storage = None
