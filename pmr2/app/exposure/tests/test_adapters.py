from unittest import TestSuite, makeSuite
from Products.CMFCore.utils import getToolByName

from pmr2.app.workspace.tests.storage import DummyStorage

from pmr2.app.exposure.content import ExposureContainer, Exposure
from pmr2.app.exposure.adapter import *

from pmr2.app.exposure.tests.base import ExposureDocTestCase


class TestAdapters(ExposureDocTestCase):

    def afterSetUp(self):
        self.portal['exposure'] = ExposureContainer('exposure')
        tester = Exposure('tester')
        self.portal.exposure['tester'] = tester

    def test_000_original_adapter(self):
        tester = self.portal.exposure.tester
        self.assertEqual(tester.workspace, None)
        tester.workspace = u'cake'
        workspace = ExposureToWorkspaceAdapter(tester)
        self.assertEqual(workspace.absolute_url_path(), 
            '/plone/workspace/cake')

    def test_001_fullpath_adapter(self):
        tester = self.portal.exposure.tester
        self.assertEqual(tester.workspace, None)
        tester.workspace = u'/plone/workspace/cake'
        workspace = ExposureToWorkspaceAdapter(tester)
        self.assertEqual(workspace.absolute_url_path(), 
            '/plone/workspace/cake')

    def test_010_original_traverse(self):
        tester = self.portal.exposure.tester
        self.assertEqual(tester.workspace, None)
        tester.workspace = u'cake'
        workspace = ExposureToWorkspaceTraverse(tester)
        self.assertEqual(workspace.absolute_url_path(), 
            '/plone/workspace/cake')

    def test_011_fullpath_traverse(self):
        tester = self.portal.exposure.tester
        self.assertEqual(tester.workspace, None)
        tester.workspace = u'/plone/workspace/cake'
        workspace = ExposureToWorkspaceTraverse(tester)
        self.assertEqual(workspace.absolute_url_path(), 
            '/plone/workspace/cake')


class TestExposureStorageAdapter(ExposureDocTestCase):
    """\
    This tests the dummy framework and implementation, along with the
    adapter with manual registration.
    """

    def setUp(self):
        ExposureDocTestCase.setUp(self)
        self.portal['exposure'] = ExposureContainer('exposure')
        self.workspace = self.portal.workspace.blank
        tester = Exposure('tester')
        tester.commit_id = u'0'
        tester.workspace = u'/plone/workspace/blank'
        self.portal.exposure['tester'] = tester
        self.exposure = self.portal.exposure['tester']

    def test_010_storage_adapter_failure(self):
        # but workspace has storage unspecified
        self.assertRaises(ValueError, ExposureStorageAdapter, self.exposure)

    def test_020_storage_adapter_success(self):
        self.workspace.storage = 'dummy_storage'
        # storage adapter should now return.
        result = ExposureStorageAdapter(self.exposure)
        self.assert_(isinstance(result, DummyStorage))
        self.assertEqual(result.rev, '0')


def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(TestAdapters))
    suite.addTest(makeSuite(TestExposureStorageAdapter))
    return suite
