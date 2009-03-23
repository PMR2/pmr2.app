from zope.interface import implements 
from plone.app.workflow.interfaces import ISharingPageRole 
from plone.app.workflow.permissions import DelegateContributorRole
from plone.app.workflow.permissions import DelegateReviewerRole

from zope.i18nmessageid import MessageFactory
_ = MessageFactory("pmr2")

import pmr2.app.security


# XXX required_permission is borrowed from plone.app.workflow for now.
class WorkspacePusherRole(object):
    implements(ISharingPageRole)
    title = _(u'title_can_push', default=u'Can hg push')
    #required_permission = 'Mercurial Push'
    required_permission = DelegateContributorRole


class ExposureCuratorRole(object):
    implements(ISharingPageRole)
    title = _(u'title_can_curate', default=u'Can curate')
    #required_permission = 'Curate Exposure'
    required_permission = DelegateReviewerRole
