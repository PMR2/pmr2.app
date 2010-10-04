from unittest import TestCase, TestSuite, makeSuite
import zope.interface
import zope.component

from pmr2.app.workspace.interfaces import *

from pmr2.app.workspace.tests.storage import DummyStorageUtility
from pmr2.app.workspace.tests.storage import DummyStorage
from pmr2.app.workspace.tests.storage import DummyWorkspace

# Objects to test

from pmr2.app.workspace.adapter import WorkspaceStorageAdapter


class TestDummyStorage(TestCase):
    """\
    This tests the dummy framework and implementation, along with the
    adapter.
    """

    def setUp(self):
        self.workspace = DummyWorkspace('test')

    def tearDown(self):
        zope.component.testing.tearDown()

    def test_000_storage(self):
        # Trivial
        storage = DummyStorage(self.workspace)
        self.assert_(isinstance(storage, DummyStorage))

    def test_001_utility(self):
        # Trivial
        utility = DummyStorageUtility()
        storage = utility(self.workspace)
        self.assert_(isinstance(storage, DummyStorage))

    def test_010_storage_base(self):
        # nothing registered
        storage = DummyStorage(self.workspace)
        # latest version should have been default
        files = storage.files()
        self.assertEqual(files, ['file1', 'file2', 'file3'])


def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(TestDummyStorage))
    return suite

