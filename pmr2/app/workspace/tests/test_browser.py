from unittest import TestCase, TestSuite, makeSuite
import zope.interface
import zope.component

from pmr2.testing.base import TestRequest

from pmr2.app.workspace.interfaces import *

# Objects to test

from pmr2.app.workspace.browser import WorkspaceTraversePage


class TestWorkspaceTraversePage(TestCase):
    """\
    This tests the dummy framework and implementation, along with the
    adapter.
    """

    def setUp(self):
        pass

    def tearDown(self):
        zope.component.testing.tearDown()

    def test_000_nothing(self):
        request = TestRequest()
        page = WorkspaceTraversePage(None, request)
        self.assertEqual(request.get('rev', None), None)
        self.assertEqual(request.get('request_subpath', None), None)

    def test_001_revision_only(self):
        request = TestRequest()
        page = WorkspaceTraversePage(None, request)
        page.publishTraverse(request, '123456')
        self.assertEqual(request.get('rev'), '123456')
        self.assertEqual(request.get('request_subpath', []))

    def test_002_revision_and_path(self):
        request = TestRequest()
        page = WorkspaceTraversePage(None, request)
        page.publishTraverse(request, '123456')
        page.publishTraverse(request, 'dir1')
        self.assertEqual(request.get('rev'), '123456')
        self.assertEqual(request.get('request_subpath'), ['dir1'])

    def test_003_revision_and_path2(self):
        request = TestRequest()
        page = WorkspaceTraversePage(None, request)
        page.publishTraverse(request, '123456')
        page.publishTraverse(request, 'dir1')
        page.publishTraverse(request, 'dir2')
        self.assertEqual(request.get('rev'), '123456')
        self.assertEqual(request.get('request_subpath'), ['dir1', 'dir2'])


def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(TestWorkspaceTraversePage))
    return suite

