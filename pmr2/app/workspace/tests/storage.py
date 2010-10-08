from os.path import basename
from datetime import datetime
import zope.interface

from pmr2.app.workspace.interfaces import IWorkspace
from pmr2.app.workspace.exceptions import *

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
        {
            'file2': 'file2-rev1\nThis is also a test.\n',
            'file3': 'Yes file1 is removed\n',
            'dir1/f1': 'first file in dir1\n',
            'dir1/f2': 'second file in dir1\n',
        },
        {
            'file1': 'file1-rev1\nThis file re-added.\n',
            'file3': 'Yes file1 is removed\n',
            'dir1/f1': 'first file in dir1\n',
            'dir1/f2': 'second file in dir1\n',
            'dir1/dir2/f1': 'first file in dir2\n',
            'dir1/dir2/f2': 'second file in dir2\n',
            'dir1/nested/file': 'some three level deep file\n',
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

    def _changeset(self, rev=None):
        if rev is None:
            rev = self.__rev

        try:
            return self._data()[rev]
        except IndexError:
            raise RevisionNotFoundError()

    def _validrev(self, rev):
        # valid type
        if not isinstance(rev, (int, basestring)):
            raise RevisionNotFoundError()
        # valid value
        try:
            rev = int(rev)
        except:
            raise RevisionNotFoundError()
        # valid revision
        self._changeset(rev)
        return rev

    @property
    def rev(self):
        return str(self.__rev)

    def checkout(self, rev):
        # set current revision
        self.__rev = self._validrev(rev)

    def files(self):
        result = self._changeset().keys()
        result.sort()
        return result

    def file(self, path):
        try:
            return self._changeset()[path]
        except KeyError:
            raise PathNotFoundError()

    def _logentry(self, rev):
        if rev < 0:
            return
        if rev == 0:
            files = self._changeset(0).keys()
            files.sort()
            return '\n'.join(['A:%s' % i for i in files])

        newcs = self._changeset(rev)
        oldcs = self._changeset(rev - 1)
        results = []
        files = set(oldcs.keys() + newcs.keys())

        for f in files:
            if f not in oldcs:
                results.append('A:%s' % f)
            elif f not in newcs:
                results.append('D:%s' % f)
            elif not oldcs[f] == newcs[f]:
                results.append('C:%s' % f)

        results.sort()
        return '\n'.join(results)

    def log(self, start, count, branch=None):
        start = self._validrev(start)
        results = []
        for i in xrange(start, start - count, -1):
            # the keys are based on mercurial.hgweb
            entry = self._logentry(i)
            if not entry:
                break
            results.append({
                'node': str(i),
                'date': str(datetime.fromtimestamp(i * 9876 + 1111111111)),
                'author': 'pmr2.teststorage <pmr2.tester@example.com>',
                'desc': entry,
            })
        return results


class DummyWorkspace(object):
    """\
    To avoid the vocab and the rest of Plone Archetypes.
    """

    zope.interface.implements(IWorkspace)

    def __init__(self, id_):
        self.id = id_
        self.storage = None
