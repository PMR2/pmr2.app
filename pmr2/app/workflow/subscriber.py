from logging import getLogger

import zope.component
from zope.component.hooks import getSite
from plone.registry.interfaces import IRegistry

from Products.CMFCore.utils import getToolByName

from pmr2.app.workflow.interfaces import ISettings

logger = getLogger(__name__)


def workflow_email(obj, event):
    registry = zope.component.getUtility(IRegistry)
    try:
        settings = registry.forInterface(ISettings,
            prefix='pmr2.app.workflow.settings')
    except KeyError:
        logger.warning('Workflow email settings not installed - '
            'pmr2.app add-on may need to be reinstalled.')
        return

    if (not settings.wf_send_email or
            not settings.wf_change_recipient or
            not settings.wf_change_states):
        return

    site = getSite()
    mail_host = getToolByName(obj, 'MailHost')
    portal_url = getToolByName(obj, 'portal_url')
    portal = portal_url.getPortalObject()
    sender = portal.getProperty('email_from_address')
    recipient = settings.wf_change_recipient

    if not event.transition.new_state_id in settings.wf_change_states:
        return

    subject = '%s `%s` is now %s' % (
        obj.portal_type, obj.title_or_id(), event.transition.new_state_id)
    message = 'Visit %s to manage.' % (obj.absolute_url())

    mail_host.send(message, recipient, sender, subject)
