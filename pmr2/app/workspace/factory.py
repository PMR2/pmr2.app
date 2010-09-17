import zope.interface
import zope.component

from pmr2.app.workspace.interfaces import IWorkspaceFileUtility


class WorkspaceFileUtility(object):
    """\
    This is a dummy object to populate the menu until something better
    can be made to replace this.
    """

    zope.interface.implements(IWorkspaceFileUtility)
