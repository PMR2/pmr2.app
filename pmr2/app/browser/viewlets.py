from zope.interface import implements
from plone.app.layout.viewlets.common import ContentActionsViewlet
from pmr2.app.browser.interfaces import IWorkspaceActionsViewlet


class WorkspaceActionsViewlet(ContentActionsViewlet):
    """\
    An ActionsViewlet for Workspaces.
    """

    implements(IWorkspaceActionsViewlet)
