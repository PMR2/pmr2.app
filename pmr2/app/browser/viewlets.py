from zope.interface import implements
from zope.component import getMultiAdapter
from plone.app.layout.viewlets.common import ContentActionsViewlet
from plone.app.layout.links.viewlets import RSSViewlet
from Products.CMFCore.utils import getToolByName

from pmr2.app.browser.interfaces import IWorkspaceActionsViewlet


class WorkspaceActionsViewlet(ContentActionsViewlet):
    """\
    An ActionsViewlet for Workspaces.
    """

    implements(IWorkspaceActionsViewlet)


class WorkspaceRSSViewlet(RSSViewlet):
    """\
    Override the update method, but keep the default template.
    """

    def update(self):
        super(RSSViewlet, self).update()
        syntool = getToolByName(self.context, 'portal_syndication')

        # we ignore the settings of the syndication tool, i.e. RSS link
        # is shown always (note the @@rsslog view is always available).
        self.allowed = True
        context_state = getMultiAdapter((self.context, self.request),
                                        name=u'plone_context_state')
        self.url = '%s/@@rsslog' % context_state.object_url()
