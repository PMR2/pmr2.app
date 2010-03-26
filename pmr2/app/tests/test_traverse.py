from unittest import TestCase, TestSuite, makeSuite
from zope.interface import implements
from zope.component import provideAdapter
from zope.interface.verify import verifyClass
from zope.publisher.interfaces import IPublishTraverse

from pmr2.app.interfaces import *
from pmr2.app.content.interfaces import *
from pmr2.app.traverse import ExposureTraverser
from pmr2.app.tests.base import TestRequest
from paste.httpexceptions import HTTPNotFound, HTTPFound


class MockWorkspace:
    def absolute_url(self):
        return 'http://nohost/mw'

mock_workspace = MockWorkspace()

class MockExposureFolder:
    implements(IExposureFolder)
    commit_id = '123'
    keys = ['valid']
    path = ''


class MockExposureSource:
    implements(IExposureSourceAdapter)

    def __init__(self, context):
        self.context = context

    def source(self):
        return self.context, mock_workspace, self.context.path


class TestExposureTraverser(TestCase):

    def setUp(self):
        def traverse(self, request, name):
            if name not in self.context.keys:
                raise AttributeError
            return name

        ExposureTraverser.o_defaultTraverse = ExposureTraverser.defaultTraverse
        ExposureTraverser.defaultTraverse = traverse
        provideAdapter(MockExposureSource, (MockExposureFolder,), 
            IExposureSourceAdapter)

    def tearDown(self):
        ExposureTraverser.defaultTraverse = ExposureTraverser.o_defaultTraverse 
        del ExposureTraverser.o_defaultTraverse 

    def traverseTester(self, traverser, request, name, location):
        traverser.publishTraverse(request, name)
        self.assertEqual(request.response.getHeader('location'), location)

    def testInterface(self):
        self.failUnless(verifyClass(IPublishTraverse, ExposureTraverser))

    def testExposureTraverser_001_valid(self):
        request = TestRequest(TraversalRequestNameStack=[])
        traverser = ExposureTraverser(MockExposureFolder(), request)
        self.assertEqual(traverser.publishTraverse(request, 'valid'), 'valid')

    def testExposureTraverser_002_standard(self):
        request = TestRequest(TraversalRequestNameStack=[])
        traverser = ExposureTraverser(MockExposureFolder(), request)
        self.traverseTester(traverser, request, 'trail',
            'http://nohost/mw/@@rawfile/123/trail')

    def testExposureTraverser_003_namestack(self):
        request = TestRequest(TraversalRequestNameStack=['f', 'u', 'n'])
        exposure = MockExposureFolder()
        traverser = ExposureTraverser(exposure, request)
        self.traverseTester(traverser, request, 'trail',
            'http://nohost/mw/@@rawfile/123/trail/f/u/n')

    def testExposureTraverser_004_subpath(self):
        request = TestRequest(TraversalRequestNameStack=[])
        exposure = MockExposureFolder()
        exposure.path = 'valid'
        traverser = ExposureTraverser(exposure, request)
        self.traverseTester(traverser, request, 'fail',
            'http://nohost/mw/@@rawfile/123/valid/fail')

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(TestExposureTraverser))
    return suite

