from unittest import TestCase, TestSuite, makeSuite
import zope.interface
import zope.component

from pmr2.app.workspace.interfaces import *
from pmr2.app.workspace.content import Workspace
from pmr2.app.workspace.storage import BaseStorage
from pmr2.app.workspace.vocab import *

from pmr2.app.workspace.test.utility import DummyStorageUtility


class TestStorageVocab(TestCase):

    def setUp(self):
        self.workspace = Workspace('test')

    def tearDown(self):
        pass

    def test_000_basic(self):
        vocab = StorageVocab(self.workspace)
        self.assertEqual(list(vocab), [])

    def test_001_single_element(self):
        zope.component.provideUtility(
            DummyStorageUtility, IStorageUtility, name='dummy_storage')
        vocab = StorageVocab(self.workspace)
        self.assertEqual(list(vocab), [('base', DummyStorageUtility)])


def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(TestStorageVocab))
    return suite

