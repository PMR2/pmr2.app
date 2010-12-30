from unittest import TestCase, TestSuite, makeSuite
import zope.interface
import zope.component

from pmr2.app.workspace.interfaces import *

from pmr2.app.workspace.tests.storage import DummyStorageUtility
from pmr2.app.workspace.tests.storage import DummyStorage
from pmr2.app.workspace.tests.storage import DummyWorkspace

# Objects to test

from pmr2.app.workspace.adapter import WorkspaceStorageAdapter


class TestWorkspaceStorageAdapter(TestCase):
    """\
    This tests the dummy framework and implementation, along with the
    adapter with manual registration.
    """

    def setUp(self):
        self.workspace = DummyWorkspace('test')

    def tearDown(self):
        zope.component.testing.tearDown()

    def test_010_storage_adapter_failure(self):
        # nothing registered
        self.assertRaises(ValueError, WorkspaceStorageAdapter, self.workspace)

    def test_011_storage_adapter_failure(self):
        # not registered, workspace has storage specified
        self.workspace.storage = 'dummy_storage'
        self.assertRaises(ValueError, WorkspaceStorageAdapter, self.workspace)

    def test_012_storage_adapter_failure(self):
        # registered, but workspace has storage unspecified
        zope.component.getSiteManager().registerUtility(
            DummyStorageUtility(), IStorageUtility, name='dummy_storage')
        self.assertRaises(ValueError, WorkspaceStorageAdapter, self.workspace)

    def test_020_storage_adapter_success(self):
        self.workspace.storage = 'dummy_storage'
        # register utility
        zope.component.getSiteManager().registerUtility(
            DummyStorageUtility(), IStorageUtility, name='dummy_storage')
        # storage adapter should now return.
        result = WorkspaceStorageAdapter(self.workspace)
        self.assert_(isinstance(result, DummyStorage))


def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(TestWorkspaceStorageAdapter))
    return suite

