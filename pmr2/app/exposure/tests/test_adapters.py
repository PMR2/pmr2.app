from unittest import TestSuite, makeSuite
from base import ExposureDocTestCase
from Products.CMFCore.utils import getToolByName

from pmr2.app.exposure.content import ExposureContainer, Exposure
from pmr2.app.exposure.adapter import *


class TestAdapters(ExposureDocTestCase):

    def afterSetUp(self):
        self.portal['exposure'] = ExposureContainer('exposure')
        tester = Exposure('tester')
        self.portal.exposure['tester'] = tester

    def test_000_original_adapter(self):
        tester = self.portal.exposure.tester
        self.assertEqual(tester.workspace, None)
        tester.workspace = u'import1'
        workspace = ExposureToWorkspaceAdapter(tester)
        self.assertEqual(workspace.absolute_url_path(), 
            '/plone/workspace/import1')

    def test_001_fullpath_adapter(self):
        tester = self.portal.exposure.tester
        self.assertEqual(tester.workspace, None)
        tester.workspace = u'/plone/workspace/import1'
        workspace = ExposureToWorkspaceAdapter(tester)
        self.assertEqual(workspace.absolute_url_path(), 
            '/plone/workspace/import1')

    def test_010_original_traverse(self):
        tester = self.portal.exposure.tester
        self.assertEqual(tester.workspace, None)
        tester.workspace = u'import1'
        workspace = ExposureToWorkspaceTraverse(tester)
        self.assertEqual(workspace.absolute_url_path(), 
            '/plone/workspace/import1')

    def test_011_fullpath_traverse(self):
        tester = self.portal.exposure.tester
        self.assertEqual(tester.workspace, None)
        tester.workspace = u'/plone/workspace/import1'
        workspace = ExposureToWorkspaceTraverse(tester)
        self.assertEqual(workspace.absolute_url_path(), 
            '/plone/workspace/import1')


def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(TestAdapters))
    return suite
