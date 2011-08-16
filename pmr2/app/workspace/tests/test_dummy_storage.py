from unittest import TestCase, TestSuite, makeSuite

import zope.component

from pmr2.app.workspace.interfaces import *
from pmr2.app.workspace.exceptions import *

from pmr2.app.workspace.tests.storage import DummyStorageUtility
from pmr2.app.workspace.tests.storage import DummyStorage
from pmr2.app.workspace.tests.storage import DummyWorkspace


class TestDummyStorage(TestCase):
    """\
    This tests the dummy framework and implementation, along with the
    adapter.
    """

    def setUp(self):
        self.workspace = DummyWorkspace('test')

    def tearDown(self):
        pass

    def filter_pathinfo(self, input):
        def filter_callable(i):
            # make sure contents is what we expect
            callables = ['contents', 'mimetype',]
            result = {}
            result.update(i)
            for c in callables:
                self.assert_(callable(result[c]))
                del result[c]
            return result

        if isinstance(input, list):
            return [filter_callable(i) for i in input]
        return filter_callable(input)

    def test_000_storage(self):
        # Direct instantiation of storage from workspace
        storage = DummyStorage(self.workspace)
        self.assert_(isinstance(storage, DummyStorage))

    def test_001_utility(self):
        # Instantiating the storage with utility
        utility = DummyStorageUtility()
        storage = utility(self.workspace)
        self.assert_(isinstance(storage, DummyStorage))

    # the adapter test is done inside test_adapter.py

    def test_010_storage_base(self):
        # nothing registered
        storage = DummyStorage(self.workspace)
        # latest version should have been default
        files = storage.files()
        self.assertEqual(files, [
            'dir1/dir2/f1', 'dir1/dir2/f2', 'dir1/f1', 'dir1/f2', 
            'dir1/nested/file', 'file1', 'file3'])

    def test_101_storage_checkout(self):
        storage = DummyStorage(self.workspace)
        storage.checkout('1')
        files = storage.files()
        self.assertEqual(files, ['file1', 'file2', 'file3'])

    def test_110_storage_checkout_revnotfound(self):
        storage = DummyStorage(self.workspace)
        self.assertRaises(RevisionNotFoundError, storage.checkout, '100')
        self.assertRaises(RevisionNotFoundError, storage.checkout, 'a00')

    def test_200_storage_log(self):
        storage = DummyStorage(self.workspace)
        result = storage.log('2', 3)
        answer = [{
            'node': '2',
            'author': 'pmr2.teststorage <pmr2.tester@example.com>',
            'date': '2005-03-18 20:27:43',
            'desc': 'A:dir1/f1\n'
                    'A:dir1/f2\n'
                    'C:file3\n'
                    'D:file1'
        },
        {
            'node': '1',
            'author': 'pmr2.teststorage <pmr2.tester@example.com>',
            'date': '2005-03-18 17:43:07',
            'desc': 'A:file3\n'
                    'C:file1\n'
                    'C:file2',
        },
        {
            'node': '0',
            'author': 'pmr2.teststorage <pmr2.tester@example.com>',
            'date': '2005-03-18 14:58:31',
            'desc': 'A:file1\n'
                    'A:file2'
        },]
        self.assertEqual(answer, result)

    def test_201_storage_log(self):
        storage = DummyStorage(self.workspace)
        result = storage.log('0', 30)
        answer = [{
            'node': '0',
            'author': 'pmr2.teststorage <pmr2.tester@example.com>',
            'date': '2005-03-18 14:58:31',
            'desc': 'A:file1\n'
                    'A:file2'
        },]
        self.assertEqual(answer, result)

    def test_250_storage_log_revnotfound(self):
        storage = DummyStorage(self.workspace)
        self.assertRaises(RevisionNotFoundError, storage.log, '100', 30)
        self.assertRaises(RevisionNotFoundError, storage.log, 'a00', 30)

    def test_300_storage_file(self):
        storage = DummyStorage(self.workspace)
        file = storage.file('file3')
        self.assertEqual(file, 'Yes file1 is removed\n')

    def test_301_storage_file(self):
        storage = DummyStorage(self.workspace)
        storage.checkout('1')
        file = storage.file('file3')
        self.assertEqual(file, 'A new test file.\n')

    def test_350_storage_file_failure_not_found(self):
        storage = DummyStorage(self.workspace)
        storage.checkout('0')
        self.assertRaises(PathNotFoundError, storage.file, 'file3')

    def test_400_fileinfo(self):
        storage = DummyStorage(self.workspace)
        storage.checkout('0')
        result = storage.fileinfo('file1')
        answer = {
            'author': 'pmr2.teststorage <pmr2.tester@example.com>',
            'permissions': '-rw-r--r--',
            'desc': '',
            'node': '0',
            'date': '2005-03-18 14:58:31',
            'size': '27',
            'basename': 'file1',
            'file': 'file1',
            'baseview': 'file',
            'contenttype': None,
            'fullpath': None,
        }
        self.assertEqual(answer, self.filter_pathinfo(result))

    def test_401_fileinfo(self):
        storage = DummyStorage(self.workspace)
        storage.checkout('3')
        result = storage.fileinfo('dir1/nested/file')
        answer = {
            'author': 'pmr2.teststorage <pmr2.tester@example.com>',
            'permissions': '-rw-r--r--',
            'desc': '',
            'node': '3',
            'date': '2005-03-18 23:12:19',
            'size': '27',
            'basename': 'file',
            'file': 'dir1/nested/file',
            'baseview': 'file',
            'contenttype': None,
            'fullpath': None,
        }
        self.assertEqual(answer, self.filter_pathinfo(result))

    def test_500_listdir_root(self):
        storage = DummyStorage(self.workspace)
        storage.checkout('3')
        result = storage.listdir('')
        answer = [
        {
            'author': '',
            'permissions': 'drwxr-xr-x',
            'desc': '',
            'node': '3',
            'date': '',
            'size': '',
            'basename': 'dir1',
            'file': 'dir1',
            'baseview': 'file',
            'contenttype': None,
            'fullpath': None,
        },
        {
            'author': 'pmr2.teststorage <pmr2.tester@example.com>',
            'permissions': '-rw-r--r--',
            'desc': '',
            'node': '3',
            'date': '2005-03-18 23:12:19',
            'size': '31',
            'basename': 'file1',
            'file': 'file1',
            'baseview': 'file',
            'contenttype': None,
            'fullpath': None,
        },
        {
            'author': 'pmr2.teststorage <pmr2.tester@example.com>',
            'permissions': '-rw-r--r--',
            'desc': '',
            'node': '3',
            'date': '2005-03-18 23:12:19',
            'size': '21',
            'basename': 'file3',
            'file': 'file3',
            'baseview': 'file',
            'contenttype': None,
            'fullpath': None,
        },
        ]
        self.assertEqual(answer, self.filter_pathinfo(result))

    def test_501_listdir_one_level(self):
        storage = DummyStorage(self.workspace)
        storage.checkout('3')
        result = storage.listdir('dir1')
        answer = [
        {
            'author': '',
            'permissions': 'drwxr-xr-x',
            'desc': '',
            'node': '3',
            'date': '',
            'size': '',
            'basename': 'dir2',
            'file': 'dir1/dir2',
            'baseview': 'file',
            'contenttype': None,
            'fullpath': None,
        },
        {
            'author': '',
            'permissions': 'drwxr-xr-x',
            'desc': '',
            'node': '3',
            'date': '',
            'size': '',
            'basename': 'nested',
            'file': 'dir1/nested',
            'baseview': 'file',
            'contenttype': None,
            'fullpath': None,
        },
        {
            'author': 'pmr2.teststorage <pmr2.tester@example.com>',
            'permissions': '-rw-r--r--',
            'desc': '',
            'node': '3',
            'date': '2005-03-18 23:12:19',
            'size': '19',
            'basename': 'f1',
            'file': 'dir1/f1',
            'baseview': 'file',
            'contenttype': None,
            'fullpath': None,
        },
        {
            'author': 'pmr2.teststorage <pmr2.tester@example.com>',
            'permissions': '-rw-r--r--',
            'desc': '',
            'node': '3',
            'date': '2005-03-18 23:12:19',
            'size': '20',
            'basename': 'f2',
            'file': 'dir1/f2',
            'baseview': 'file',
            'contenttype': None,
            'fullpath': None,
        },
        ]
        self.assertEqual(answer, self.filter_pathinfo(result))
        # include trailing /
        result = storage.listdir('dir1/')
        self.assertEqual(answer, self.filter_pathinfo(result))

    def test_502_listdir_two_levels(self):
        storage = DummyStorage(self.workspace)
        storage.checkout('3')
        result = storage.listdir('dir1/nested')
        answer = [
        {
            'author': 'pmr2.teststorage <pmr2.tester@example.com>',
            'permissions': '-rw-r--r--',
            'desc': '',
            'node': '3',
            'date': '2005-03-18 23:12:19',
            'size': '27',
            'basename': 'file',
            'file': 'dir1/nested/file',
            'baseview': 'file',
            'contenttype': None,
            'fullpath': None,
        }]
        self.assertEqual(answer, self.filter_pathinfo(result))
        # include multiple /
        result = storage.listdir('dir1///nested')
        self.assertEqual(answer, self.filter_pathinfo(result))

    def test_510_listdir_on_file_fail(self):
        storage = DummyStorage(self.workspace)
        storage.checkout('3')
        self.assertRaises(PathNotDirError, storage.listdir, 'file1')
        self.assertRaises(PathNotDirError, storage.listdir, 'dir1/f1')
        self.assertRaises(PathNotDirError, storage.listdir, 'dir1/dir2/f1')

    def test_511_listdir_on_non_path(self):
        storage = DummyStorage(self.workspace)
        storage.checkout('3')
        self.assertRaises(PathNotFoundError, storage.listdir, 'file11')
        self.assertRaises(PathNotFoundError, storage.listdir, 'dir1/f11')
        self.assertRaises(PathNotFoundError, storage.listdir, 'dir1/dir2/f11')
        self.assertRaises(PathNotFoundError, storage.listdir, 'dir2/dir1/f11')

    def test_600_pathinfo(self):
        storage = DummyStorage(self.workspace)
        storage.checkout('0')
        result = storage.pathinfo('file1')
        answer = {
            'author': 'pmr2.teststorage <pmr2.tester@example.com>',
            'permissions': '-rw-r--r--',
            'desc': '',
            'node': '0',
            'date': '2005-03-18 14:58:31',
            'size': '27',
            'basename': 'file1',
            'file': 'file1',
            'baseview': 'file',
            'contenttype': None,
            'fullpath': None,
        }
        self.assertEqual(answer, self.filter_pathinfo(result))
        self.assert_(result['mimetype']().startswith('text/plain'))

    def test_601_pathinfo_nested_dir(self):
        storage = DummyStorage(self.workspace)
        storage.checkout('3')
        result = storage.pathinfo('dir1/nested')
        answer = {
            'author': '',
            'permissions': 'drwxr-xr-x',
            'desc': '',
            'node': '3',
            'date': '',
            'size': '',
            'basename': 'nested',
            'file': 'dir1/nested',
            'baseview': 'file',
            'contenttype': None,
            'fullpath': None,
        }
        self.assertEqual(answer, self.filter_pathinfo(result))

    def test_602_pathinfo_nested_dir(self):
        storage = DummyStorage(self.workspace)
        storage.checkout('3')
        result = storage.pathinfo('dir1/nested/file')
        answer = {
            'author': 'pmr2.teststorage <pmr2.tester@example.com>',
            'permissions': '-rw-r--r--',
            'desc': '',
            'node': '3',
            'date': '2005-03-18 23:12:19',
            'size': '27',
            'basename': 'file',
            'file': 'dir1/nested/file',
            'baseview': 'file',
            'contenttype': None,
            'fullpath': None,
        }
        self.assertEqual(answer, self.filter_pathinfo(result))

    def test_700_archiveFormats(self):
        storage = DummyStorage(self.workspace)
        formats = storage.archiveFormats
        self.assertEqual(formats, ['dummy'])

    def test_710_archiveInfo(self):
        storage = DummyStorage(self.workspace)
        info = storage.archiveInfo('dummy')
        self.assertEqual(info, {
            'name': 'Dummy Archive',
            'ext': '.dummy',
            'mimetype': 'application/x-dummy',
        })

    def test_711_archiveInfoValueError(self):
        storage = DummyStorage(self.workspace)
        self.assertRaises(ValueError, storage.archiveInfo, 'invalid')

    def test_720_archive(self):
        storage = DummyStorage(self.workspace)
        archive = storage.archive('dummy')
        self.assert_(archive.startswith('(dp1\nS'))


def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(TestDummyStorage))
    return suite

