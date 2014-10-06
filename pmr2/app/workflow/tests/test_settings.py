import unittest
import warnings

import zope.component

from zExceptions import Unauthorized
from Products.PloneTestCase.setup import portal_owner, default_password
from Products.PloneTestCase import ptc
from Products.Five.testbrowser import Browser
from plone.registry.interfaces import IRegistry

from pmr2.testing.base import TestRequest

from pmr2.app.workflow.interfaces import ISettings
from pmr2.app.workflow.browser import SettingsEditForm


class SettingsTestCase(ptc.FunctionalTestCase):
    """
    Test that the settings is set up correctly.
    """

    def afterSetUp(self):
        self.registry = zope.component.getUtility(IRegistry)
        self.settings = self.registry.forInterface(ISettings,
            prefix='pmr2.app.workflow.settings')

    def test_basic_render_form(self):
        request = TestRequest()
        form = SettingsEditForm(self.portal, request)
        form.update()
        result = form.render()
        self.assertTrue(result)

    def test_edit_field(self):
        request = TestRequest(form={
            'form.widgets.wf_change_recipient': 'user@example.com',
            'form.widgets.wf_send_email': 'selected',
            'form.buttons.apply': 1,
        })
        form = SettingsEditForm(self.portal, request)
        form.update()
        self.assertEqual(self.settings.wf_change_recipient, 'user@example.com')
        self.assertTrue(self.settings.wf_send_email)

    def test_render_field(self):
        self.settings.wf_change_recipient = u'tester@example.com'

        request = TestRequest()
        form = SettingsEditForm(self.portal, request)
        form.update()
        result = form.render()
        self.assertIn('tester@example.com', result)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(SettingsTestCase))
    return suite
