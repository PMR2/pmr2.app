from unittest import TestCase, TestSuite, makeSuite

import zope.interface
import zope.component
from plone.z3cform.fieldsets import extensible
from plone.z3cform import tests

from pmr2.app.exposure.browser.workspace import ExtensibleAddForm
from pmr2.testing.base import TestRequest


class D(ExtensibleAddForm):
    disableAuthenticator = True
    added = 0
    extended = False
    def add(self, *a, **kw):
        self.added = self.added + 1
    def create(self, *a, **kw):
        return object()

class E(extensible.FormExtender):
    zope.component.adapts(zope.interface.Interface, TestRequest, D)
    def update(self):
        self.form.extended = True


class TestBrowserWorkspace(TestCase):
    """
    Tests for some of the base classes.
    """

    def setUp(self):
        tests.setup_defaults()
        zope.component.provideAdapter(factory=E, name=u'test.extender')
        self.req = TestRequest(form={'form.buttons.add': 1})
        self.form = D(object(), self.req)

    def test_no_double_add(self):
        self.form.update()
        self.assertTrue(self.form.extended)
        self.assertEqual(self.form.added, 1)


def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(TestBrowserWorkspace))
    return suite

