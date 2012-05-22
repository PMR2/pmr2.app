from zope.component import getMultiAdapter

from AccessControl import Unauthorized
from Products.CMFCore.utils import getToolByName

from pmr2.app.workspace.exceptions import *
from pmr2.app.browser.layout import FormWrapper


class WorkspaceProtocolWrapper(FormWrapper):
    """\
    Form wrapper for interaction with the protocol of the storage
    backend for the given workspace context.
    """

    def render(self):
        if self.form_instance.protocolView.enabled():
            # the wrapper's update method actually called form_instance
            # render method already with output assigned to this 
            # variable.
            return self.contents
        return super(WorkspaceProtocolWrapper, self).render()


class BorderedWorkspaceProtocolWrapper(WorkspaceProtocolWrapper):
    """\
    Workspace default view uses this for the menu.
    """

    def __init__(self, *a, **kw):
        super(BorderedWorkspaceProtocolWrapper, self).__init__(*a, **kw)
        self.request['enable_border'] = True
