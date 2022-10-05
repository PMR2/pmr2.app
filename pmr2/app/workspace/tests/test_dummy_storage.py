from unittest import TestCase, TestSuite, makeSuite
from os.path import dirname, join

import zope.component
from plone.registry.interfaces import IRegistry

import pmr2.testing

from pmr2.app.workspace.interfaces import *
from pmr2.app.workspace.exceptions import *

from pmr2.app.workspace.tests import base
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

    def test_005_empty_storage(self):
        # Direct instantiation of storage from workspace
        workspace = DummyWorkspace('broken_empty')
        DummyStorageUtility().create(workspace, _empty=True)
        storage = DummyStorage(workspace)
        self.assertIsNone(storage.rev)
        self.assertEqual([], storage.roots())

    # the adapter test is done inside test_adapter.py

    def test_010_storage_base(self):
        # nothing registered
        storage = DummyStorage(self.workspace)
        # latest version should have been default
        files = storage.files()
        self.assertEqual(files, [
            'dir1/dir2/f1', 'dir1/dir2/f2', 'dir1/f1', 'dir1/f2', 
            'dir1/nested/file', 'file1', 'file3'])
        self.assertEqual(storage.roots(), ['0'])

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
            'external': None,
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
            'external': None,
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
            'external': None,
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
            'external': None,
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
            'external': None,
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
            'external': None,
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
            'external': None,
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
            'external': None,
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
            'external': None,
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
            'external': None,
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
            'external': None,
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
            'external': None,
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
            'external': None,
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

    def test_800_sync_identifier(self):
        # mostly a dummy at this stage.
        utility = DummyStorageUtility()
        newworkspace = DummyWorkspace('new')
        utility.syncIdentifier(newworkspace, 'cake')

        storage = DummyStorage(newworkspace)
        storage.checkout()
        self.assert_('null' in storage.files())

    def test_801_sync_workspace(self):
        # mostly a dummy at this stage.
        utility = DummyStorageUtility()
        new2 = DummyWorkspace('new2')
        cake = DummyWorkspace('cake')
        utility.syncWorkspace(new2, cake)

        storage = DummyStorage(new2)
        storage.checkout()
        self.assert_('null' in storage.files())

    def test_900_external(self):
        # mostly a dummy at this stage.
        utility = DummyStorageUtility()
        external_root = DummyWorkspace('external_root')
        external_test = DummyWorkspace('external_test')
        storage_root = DummyStorage(external_root)
        storage_test = DummyStorage(external_test)

        result = storage_root.pathinfo('external_test')
        self.assertEqual(result['external'], {
            '': '_subrepo',
            'path': '',
            'rev': '0',
            'location': 'http://nohost/plone/workspace/external_test',
        })

        result = storage_root.pathinfo('external_test/test.txt')
        self.assertEqual(result['external'], {
            '': '_subrepo',
            'path': 'test.txt',
            'rev': '0',
            'location': 'http://nohost/plone/workspace/external_test',
        })

        # valid files don't get this perk.
        with self.assertRaises(PathNotFoundError):
            storage_root.file('external_test/test.txt')

        # since not registered.
        with self.assertRaises(PathNotFoundError):
            storage_root.resolve_file('external_test/test.txt'),

    def test_950_loader(self):
        # Test loading from filesystem.
        target = join(dirname(pmr2.testing.__file__), 'data', 'rdfmodel')
        utility = DummyStorageUtility()
        utility._loadDir('rdfmodel', target)

        self.assertTrue('rdfmodel' in utility._dummy_storage_data)
        self.assertEqual(len(utility._dummy_storage_data['rdfmodel']), 4)

        self.assertEqual(len(utility._dummy_storage_data['rdfmodel'][0]), 2)
        self.assertEqual(len(utility._dummy_storage_data['rdfmodel'][0].get(
            'component/module.cellml')), 4197)

        self.assertEqual(len(utility._dummy_storage_data['rdfmodel'][1]), 5)
        self.assertEqual(len(utility._dummy_storage_data['rdfmodel'][1].get(
            'example_model.cellml')), 4288)

        self.assertEqual(utility._dummy_storage_data['rdfmodel'][2].get(
            'component/README'),
                'This is a readme file inside the component directory.\n')

        self.assertEqual(len(utility._dummy_storage_data['rdfmodel'][3].get(
            'component/module.cellml')), 4197)


class TestSiteDummyStorage(base.WorkspaceBrowserDocTestCase):
    """
    Collection of miscellaneous tests.
    """

    def setUp(self):
        super(TestSiteDummyStorage, self).setUp()
        self.makeExternalWorkspace()

    def test_0001_external(self):
        storage_root = IStorage(self.portal.workspace.external_root)
        storage_test = IStorage(self.portal.workspace.external_test)

        result = storage_root.pathinfo('external_test')
        self.assertEqual(result['external'], {
            '': '_subrepo',
            'path': '',
            'rev': '0',
            'location': 'http://nohost/plone/workspace/external_test',
        })

        result = storage_root.pathinfo('external_test/test.txt')
        self.assertEqual(result['external'], {
            '': '_subrepo',
            'path': 'test.txt',
            'rev': '0',
            'location': 'http://nohost/plone/workspace/external_test',
        })

        # valid files don't get this perk.
        with self.assertRaises(PathNotFoundError):
            storage_root.file('external_test/test.txt')

        # due to no registry entry for nohost
        with self.assertRaises(SubrepoPathUnsupportedError) as exc:
            storage_root.resolve_file('external_test/test.txt'),
        self.assertEqual(
            exc.exception.args[0],
            "requested path at 'external_test/test.txt' requires subrepo at "
            "unsupported netloc 'nohost' when trying to resolve subpath "
            "'test.txt'"
        )

        registry = zope.component.getUtility(IRegistry)
        registry['pmr2.app.settings.prefix_maps'] = {u'nohost': u''}
        self.assertEqual(
            storage_root.resolve_file('external_test/test.txt'),
            'external test file.\n',
        )


def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(TestDummyStorage))
    suite.addTest(makeSuite(TestSiteDummyStorage))
    return suite

