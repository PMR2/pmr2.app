from zope.interface import implementer
from pmr2.app.workspace.interfaces import IWorkspaceStorageIncomingEvent


class WorkspaceEvent(object):
    """
    Base workspace event.
    """

    def __init__(self, workspace):
        self.object = self.workspace = workspace


@implementer(IWorkspaceStorageIncomingEvent)
class Push(WorkspaceEvent):
    """
    Push from external source modifying storage contents.
    """
