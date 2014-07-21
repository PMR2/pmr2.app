from unittest import TestCase, TestSuite, makeSuite
import zope.interface
import zope.component

from pmr2.app.workspace.interfaces import *

from pmr2.app.workspace.tests.storage import LegacyDummyStorageUtility
from pmr2.app.workspace.tests.storage import DummyStorageUtility
from pmr2.app.workspace.tests.storage import DummyStorage
from pmr2.app.workspace.tests.storage import DummyWorkspace

# Objects to test

from pmr2.app.workspace.adapter import WorkspaceStorageAdapter
from pmr2.app.workspace.adapter import StorageProtocolAdapter

from pmr2.testing.base import TestRequest


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


class StorageProtocolAdapaterTestCase(TestCase):
    """
    Test that the code generates the correct events based on current and
    legacy return values.
    """

    def setUp(self):
        self.workspace = DummyWorkspace('test')
        self.workspace.storage = 'dummy_storage'

        # register utilities
        zope.component.getSiteManager().registerUtility(
            DummyStorageUtility(), IStorageUtility, name='dummy_storage')
        zope.component.getSiteManager().registerUtility(
            LegacyDummyStorageUtility(), IStorageUtility,
            name='legacy_dummy_storage')

    def tearDown(self):
        zope.component.testing.tearDown()

    def test_storage_protocol_default(self):
        # standard GET request
        request = TestRequest(form={'cmd': 'revcount'})
        # storage adapter should now return.
        pa = StorageProtocolAdapter(self.workspace, request)
        result = pa()
        self.assertEqual(result.result, '4')
        self.assertEqual(result.event, None)

    def test_storage_protocol_legacy(self):
        self.workspace.storage = 'legacy_dummy_storage'
        # defaults to POST
        request = TestRequest(form={'cmd': 'revcount'})
        # request.method = 'POST'

        # storage adapter should now return.
        pa = StorageProtocolAdapter(self.workspace, request)
        result = pa()
        self.assertEqual(result.result, '4')
        self.assertEqual(result.event.workspace, self.workspace)

    def test_storage_protocol_legacy_get(self):
        self.workspace.storage = 'legacy_dummy_storage'
        # force request to GET
        request = TestRequest(form={'cmd': 'revcount'})
        request.method = 'GET'
        # storage adapter should now return.
        pa = StorageProtocolAdapter(self.workspace, request)
        result = pa()
        self.assertEqual(result.result, '4')
        self.assertEqual(result.event, None)

    def test_storage_protocol_push(self):
        request = TestRequest(form={'cmd': 'update'})
        # storage adapter should now return.
        pa = StorageProtocolAdapter(self.workspace, request)
        result = pa()
        self.assertEqual(result.result, 'Updated')
        self.assertEqual(result.event.workspace, self.workspace)

    def test_storage_protocol_push_legacy(self):
        self.workspace.storage = 'legacy_dummy_storage'
        request = TestRequest(form={'cmd': 'update'})
        # storage adapter should now return.
        pa = StorageProtocolAdapter(self.workspace, request)
        result = pa()
        self.assertEqual(result.result, 'Updated')
        self.assertEqual(result.event.workspace, self.workspace)


def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(TestWorkspaceStorageAdapter))
    suite.addTest(makeSuite(StorageProtocolAdapaterTestCase))
    return suite

