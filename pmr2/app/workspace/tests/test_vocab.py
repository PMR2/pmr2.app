from unittest import TestCase, TestSuite, makeSuite
import zope.interface
import zope.component

from pmr2.app.workspace.interfaces import *
from pmr2.app.workspace.content import Workspace
from pmr2.app.workspace.storage import BaseStorage
from pmr2.app.workspace.vocab import *
from pmr2.app.workspace.adapter import WorkspaceStorageAdapter

from pmr2.app.workspace.tests.storage import DummyStorageUtility
from pmr2.app.workspace.tests.storage import DummyWorkspace


class TestStorageVocab(TestCase):

    def setUp(self):
        self.workspace = Workspace('test')

    def tearDown(self):
        zope.component.testing.tearDown()

    def test_000_basic(self):
        vocab = StorageVocab(self.workspace)
        self.assertEqual(list(vocab), [])

    def test_001_single_element(self):
        zope.component.getSiteManager().registerUtility(
            DummyStorageUtility(), IStorageUtility, name='dummy_storage')
        vocab = StorageVocab(self.workspace)
        self.assertEqual(vocab.getTerm('dummy_storage').title, 'Dummy Storage')


class TestManifestListVocab(TestCase):

    def setUp(self):
        self.workspace = DummyWorkspace('test')
        self.workspace.storage = 'dummy_storage'
        zope.component.getSiteManager().registerUtility(
            DummyStorageUtility(), IStorageUtility, name='dummy_storage')
        zope.component.getSiteManager().registerAdapter(
            WorkspaceStorageAdapter, (IWorkspace,), IStorage)

    def tearDown(self):
        zope.component.testing.tearDown()

    def test_000_basic(self):
        vocab = ManifestListVocab(self.workspace)
        # just a basic assertion that the list of files is retrieved.
        self.assertEqual(vocab.getTerm('file1').value, 'file1')


def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(TestStorageVocab))
    suite.addTest(makeSuite(TestManifestListVocab))
    return suite

