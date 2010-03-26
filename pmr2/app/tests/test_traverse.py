from unittest import TestCase, TestSuite, makeSuite
from zope.interface import implements
from zope.component import provideAdapter
from zope.interface.verify import verifyClass
from zope.publisher.interfaces import IPublishTraverse
from paste.httpexceptions import HTTPNotFound, HTTPFound

from pmr2.app.interfaces import *
from pmr2.app.content.interfaces import *
from pmr2.app.content import ExposureContainer, Exposure
from pmr2.app.traverse import *
from pmr2.app.tests.base import TestRequest, ExposureDocTestCase


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
        # note that namestack is usuall found reversed.
        request = TestRequest(TraversalRequestNameStack=['n', 'u', 'f'])
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


class TestExposureContainerTraverser(ExposureDocTestCase):

    def afterSetUp(self):
        ids = ['abcded', 'abcdee', 'abcdef', 'abcccf', '111111']
        def traverse(self, request, name):
            if name not in ids:
                raise AttributeError
            return name

        ExposureContainerTraverser.o_defaultTraverse = \
            ExposureContainerTraverser.defaultTraverse
        ExposureContainerTraverser.o_base_query = \
            ExposureContainerTraverser.base_query

        ExposureContainerTraverser.defaultTraverse = traverse
        ExposureContainerTraverser.base_query = {'portal_type': 'Exposure'}

        self.portal['exposure'] = ExposureContainer('exposure')
        for i in ids:
            self.portal.exposure[i] = Exposure(i)
            self.portal.exposure[i].reindexObject()

        self.context = self.portal.exposure

    def beforeTearDown(self):
        ExposureContainerTraverser.defaultTraverse = \
            ExposureContainerTraverser.o_defaultTraverse 
        ExposureContainerTraverser.base_query = \
            ExposureContainerTraverser.o_base_query 
        del ExposureContainerTraverser.o_defaultTraverse 
        del ExposureContainerTraverser.o_base_query 

    def testInterface(self):
        self.failUnless(verifyClass(IPublishTraverse, 
            ExposureContainerTraverser))

    def testExposureContainerTraverser_001_valid(self):
        request = TestRequest(TraversalRequestNameStack=[])
        traverser = ExposureContainerTraverser(self.context, request)
        self.assertEqual(traverser.publishTraverse(request, 'abcded'), 
            'abcded')

    def testExposureContainerTraverser_002_toomany(self):
        request = TestRequest(TraversalRequestNameStack=[])
        traverser = ExposureContainerTraverser(self.context, request)
        self.assertRaises(HTTPNotFound, traverser.publishTraverse, request,
            'abcde')

    def testExposureContainerTraverser_002_one(self):
        request = TestRequest(TraversalRequestNameStack=[])
        traverser = ExposureContainerTraverser(self.context, request)
        traverser.publishTraverse(request, '1')
        self.assertEqual(request.response.getHeader('location'), 
            'http://nohost/plone/exposure/111111')

    def testExposureContainerTraverser_003_fine_with_subpath(self):
        request = TestRequest(TraversalRequestNameStack=['@@view', 'test'])
        traverser = ExposureContainerTraverser(self.context, request)
        traverser.publishTraverse(request, 'abcc')
        self.assertEqual(request.response.getHeader('location'), 
            'http://nohost/plone/exposure/abcccf/test/@@view')


def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(TestExposureTraverser))
    suite.addTest(makeSuite(TestExposureContainerTraverser))
    return suite

