from zope.interface import implements 
from plone.app.workflow.interfaces import ISharingPageRole 

from zope.i18nmessageid import MessageFactory
_ = MessageFactory("pmr2")

import pmr2.app.security


class WorkspacePusherRole(object):
    implements(ISharingPageRole)
    title = _(u'title_can_push', default=u'Can hg push')
    required_permission = 'Mercurial Push'
