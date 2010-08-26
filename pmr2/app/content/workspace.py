from zope import interface
from zope.schema import fieldproperty
import zope.component

from Acquisition import aq_parent, aq_inner
from Products.CMFCore.permissions import View
from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin
from Products.ATContentTypes.content.folder import ATFolder, ATBTreeFolder
from Products.ATContentTypes.content.document import ATDocument
from Products.Archetypes import atapi

import pmr2.mercurial.interfaces
import pmr2.mercurial.utils

from pmr2.app.interfaces import IPMR2GlobalSettings
from pmr2.app.content.interfaces import *
from pmr2.app.interfaces.exceptions import *


class WorkspaceContainer(ATBTreeFolder):
    """\
    Container for workspaces in PMR2.
    """

    interface.implements(IWorkspaceContainer)

    # title is defined by ATFolder

    def __init__(self, oid='workspace', **kwargs):
        super(WorkspaceContainer, self).__init__(oid, **kwargs)


class Workspace(BrowserDefaultMixin, atapi.BaseContent):
    """\
    PMR2 Workspace object is used to connect to the repository of model
    and related data.
    """

    interface.implements(
        IWorkspace, 
        pmr2.mercurial.interfaces.IPMR2StorageBase,
    )

    description = fieldproperty.FieldProperty(IWorkspace['description'])
