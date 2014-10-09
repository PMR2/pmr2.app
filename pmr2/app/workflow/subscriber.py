from collections import defaultdict
from logging import getLogger
import re

import zope.component
from zope.component.hooks import getSite
from plone.registry.interfaces import IRegistry

from Products.CMFCore.utils import getToolByName

from pmr2.app.workflow.interfaces import ISettings

logger = getLogger(__name__)

_p = re.compile('{(\w*)')

prefix = 'pmr2.app.workflow.settings'

def format(settings, key, params):
    s = getattr(settings, key)
    try:
        return _p.sub('{0[\\1]', s).format(params)
    except:
        logger.warning('%s.%s failed to be properly formatted - sending as-is',
            prefix, key)
        return s

def workflow_email(obj, event):
    registry = zope.component.getUtility(IRegistry)
    try:
        settings = registry.forInterface(ISettings, prefix=prefix)
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

    params = defaultdict(str, {
        'obj': obj,
        'event': event,
        'obj_url': obj.absolute_url(),
        'title_or_id': obj.title_or_id(),
        'portal_url': portal.portal_url(),
    })

    subject = format(settings, 'subject_template', params)
    message = format(settings, 'message_template', params)

    mail_host.send(message, recipient, sender, subject)
