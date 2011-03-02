import zope.interface
import zope.component

from zope.schema import fieldproperty

from Acquisition import aq_parent, aq_inner
from Products.CMFCore.permissions import View
from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin
from Products.ATContentTypes.content.folder import ATFolder, ATBTreeFolder
from Products.ATContentTypes.content.document import ATDocument
from Products.Archetypes import atapi

from pmr2.app.interfaces import IPMR2GlobalSettings
from pmr2.app.interfaces.exceptions import *

from pmr2.app.workspace.interfaces import *


class WorkspaceContainer(ATBTreeFolder):
    """\
    Container for workspaces in PMR2.
    """

    zope.interface.implements(IWorkspaceContainer)

    # title is defined by ATFolder

    def __init__(self, oid='workspace', **kwargs):
        super(WorkspaceContainer, self).__init__(oid, **kwargs)


class Workspace(BrowserDefaultMixin, atapi.BaseContent):
    """\
    PMR2 Workspace object is used to connect to the repository of model
    and related data.
    """

    zope.interface.implements(IWorkspace)

    description = fieldproperty.FieldProperty(IWorkspace['description'])
    storage = fieldproperty.FieldProperty(IWorkspace['storage'])


atapi.registerType(WorkspaceContainer, 'pmr2.app.workspace')
atapi.registerType(Workspace, 'pmr2.app.workspace')
