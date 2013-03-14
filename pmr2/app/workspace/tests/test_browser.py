from unittest import TestCase, TestSuite, makeSuite
import zope.interface
import zope.component

from pmr2.testing.base import TestRequest

from pmr2.app.workspace.interfaces import *

# Objects to test

from pmr2.app.workspace.browser import browser
from pmr2.app.workspace.browser.util import set_xmlbase
from pmr2.app.workspace.browser.util import obfuscate

from pmr2.app.workspace.tests import base


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
        page = browser.WorkspaceTraversePage(None, request)
        self.assertEqual(request.get('rev', None), None)
        self.assertEqual(request.get('request_subpath', None), None)

    def test_001_revision_only(self):
        request = TestRequest()
        page = browser.WorkspaceTraversePage(None, request)
        page.publishTraverse(request, '123456')
        self.assertEqual(request.get('rev'), '123456')
        self.assertEqual(request.get('request_subpath'), [])

    def test_002_revision_and_path(self):
        request = TestRequest()
        page = browser.WorkspaceTraversePage(None, request)
        page.publishTraverse(request, '123456')
        page.publishTraverse(request, 'dir1')
        self.assertEqual(request.get('rev'), '123456')
        self.assertEqual(request.get('request_subpath'), ['dir1'])

    def test_003_revision_and_path2(self):
        request = TestRequest()
        page = browser.WorkspaceTraversePage(None, request)
        page.publishTraverse(request, '123456')
        page.publishTraverse(request, 'dir1')
        page.publishTraverse(request, 'dir2')
        self.assertEqual(request.get('rev'), '123456')
        self.assertEqual(request.get('request_subpath'), ['dir1', 'dir2'])


class TestWorkspaceBrowserUtil(TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_001_set_xmlbase(self):
        input = (
            '<?xml version="1.0" encoding="utf-8"?>\n'
            '<rdf:RDF \n'
            '  xmlns:pcenv="http://www.cellml.org/tools/pcenv/"\n'
            '  xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"\n'
            '>\n'
            ' <rdf:Description rdf:about="#element" pcenv:colour="#aef16d">\n'
            '   <pcenv:x-variable rdf:resource="#xvar"/>\n'
            '   <pcenv:y-variable rdf:resource="#yvar"/>\n'
            ' </rdf:Description>\n'
            '</rdf:RDF>\n'
        )
        uri = 'http://example.com/'
        output = set_xmlbase(input, uri)
        self.assert_(
            output.splitlines()[1].endswith('xml:base="http://example.com/">'))

    def test_002_obfuscate(self):
        input = 'user@example.com'
        output = obfuscate(input)
        self.assertNotEqual(input, output)


class WorkspaceViewTestCase(base.WorkspaceBrowserDocTestCase):
    """
    Collection of miscellaneous tests.
    """

    def setUp(self):
        super(WorkspaceViewTestCase, self).setUp()
        self.makeExternalWorkspace()

    def test_embedded_redirect(self):
        request = TestRequest()
        page = browser.FilePage(self.portal.workspace.external_root, request)
        page.publishTraverse(request, '0')
        page.publishTraverse(request, 'external_test')
        self.assertEqual(page(), '')
        self.assertEqual(request.response.getHeader('location'),
            'http://nohost/plone/workspace/external_test/rawfile/0/')

        self.testbrowser.open(self.portal.absolute_url() +
            '/workspace/external_root/file/0/external_test')
        self.assertEqual(self.testbrowser.url, 
            'http://nohost/plone/workspace/external_test/file/0/')

    def test_embedded_redirect_file(self):
        request = TestRequest()
        page = browser.FilePage(self.portal.workspace.external_root, request)
        page.publishTraverse(request, '0')
        page.publishTraverse(request, 'external_test/test.txt')
        self.assertEqual(page(), '')
        self.assertEqual(request.response.getHeader('location'),
            'http://nohost/plone/workspace/external_test/rawfile/0/test.txt')

        self.testbrowser.open(self.portal.absolute_url() +
            '/workspace/external_root/rawfile/0/external_test/test.txt')
        self.assertEqual(self.testbrowser.url, 
            'http://nohost/plone/workspace/external_test/rawfile/0/test.txt')

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(TestWorkspaceTraversePage))
    suite.addTest(makeSuite(TestWorkspaceBrowserUtil))
    suite.addTest(makeSuite(WorkspaceViewTestCase))
    return suite

