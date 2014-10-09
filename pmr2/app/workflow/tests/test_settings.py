import unittest
import warnings

import zope.component

from Acquisition import aq_base
from Products.CMFCore.utils import getToolByName
from Products.PloneTestCase import ptc
from Products.MailHost.interfaces import IMailHost
from Products.CMFPlone.tests.utils import MockMailHost
from plone.registry.interfaces import IRegistry

from plone.app.testing import TEST_USER_ID, setRoles

from pmr2.testing.base import TestRequest
from pmr2.app.workspace.tests.layer import WORKSPACE_INTEGRATION_LAYER

from pmr2.app.workflow.interfaces import ISettings
from pmr2.app.workflow.browser import SettingsEditForm
from pmr2.app.workflow.subscriber import workflow_email



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


class MailTestCase(unittest.TestCase):
    """
    Test to see that emails are sent.
    """

    layer = WORKSPACE_INTEGRATION_LAYER

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

        self.registry = zope.component.getUtility(IRegistry)
        self.settings = self.registry.forInterface(ISettings,
            prefix='pmr2.app.workflow.settings')
        self.settings.wf_change_recipient = u'tester@example.com'
        self.settings.wf_send_email = True

        self.portal._original_MailHost = self.portal.MailHost
        self.portal.MailHost = mailhost = MockMailHost('MailHost')
        sm = zope.component.getSiteManager(context=self.portal)
        sm.unregisterUtility(provided=IMailHost)
        sm.registerUtility(mailhost, provided=IMailHost)
        # We need to fake a valid mail setup
        self.portal.email_from_address = 'admin@example.com'
        self.mailhost = self.portal.MailHost

    def tearDown(self):
        self.portal.MailHost = self.portal._original_MailHost
        sm = zope.component.getSiteManager(context=self.portal)
        sm.unregisterUtility(provided=IMailHost)
        sm.registerUtility(aq_base(self.portal._original_MailHost),
                           provided=IMailHost)

    def test_workflow_email_success(self):
        self.settings.wf_change_states = [u'pending']
        pw = getToolByName(self.portal, "portal_workflow")
        pw.doActionFor(self.portal.workspace.test, "submit")
        msg = str(self.mailhost.messages[0])
        self.assertTrue('Subject: Workspace `test` is now pending' in msg)
        self.assertTrue('To: tester@example.com' in msg)
        self.assertTrue('From: admin@example.com' in msg)
        self.assertTrue('Visit http://nohost/plone/workspace/test' in msg)

    def test_workflow_email_custom_format_success(self):
        self.settings.wf_change_states = [u'published']
        self.settings.subject_template = u'Item: ({not_exist})'
        self.settings.message_template = (u'{obj.id} is now '
            '{event.transition.new_state_id} at site <{portal_url}>.')

        pw = getToolByName(self.portal, "portal_workflow")
        pw.doActionFor(self.portal.workspace.cake, "publish")
        msg = str(self.mailhost.messages[0])
        self.assertTrue('Subject: Item: ()' in msg)
        self.assertTrue('To: tester@example.com' in msg)
        self.assertTrue('From: admin@example.com' in msg)
        self.assertTrue('cake is now published at site <http://nohost/plone>.'
            in msg)

    def test_workflow_email_custom_format_malformed(self):
        self.settings.wf_change_states = [u'published']
        self.settings.subject_template = u'Item: not_exist}'
        self.settings.message_template = \
            u'{obj.not_attribute} is now {event.transition.new_state_id}'
        pw = getToolByName(self.portal, "portal_workflow")
        pw.doActionFor(self.portal.workspace.cake, "publish")
        msg = str(self.mailhost.messages[0])
        # None of the message templates will be processed here.
        self.assertTrue(self.settings.subject_template in msg)
        self.assertTrue(self.settings.message_template in msg)

    def test_workflow_email_skipped_wf_state(self):
        self.settings.wf_change_states = [u'pending']
        pw = getToolByName(self.portal, "portal_workflow")
        pw.doActionFor(self.portal.workspace.test, "publish")
        self.assertEqual(len(self.mailhost.messages), 0)

    def test_workflow_email_not_in_state(self):
        pw = getToolByName(self.portal, "portal_workflow")
        pw.doActionFor(self.portal.workspace.test, "submit")
        self.assertEqual(len(self.mailhost.messages), 0)

    def test_workflow_email_disabled(self):
        self.settings.wf_send_email = False
        pw = getToolByName(self.portal, "portal_workflow")
        pw.doActionFor(self.portal.workspace.test, "submit")
        self.assertEqual(len(self.mailhost.messages), 0)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(SettingsTestCase))
    suite.addTest(makeSuite(MailTestCase))
    return suite
