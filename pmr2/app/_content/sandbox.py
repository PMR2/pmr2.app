import os.path

from zope import interface
from zope.schema import fieldproperty

from AccessControl import ClassSecurityInfo
from Acquisition import aq_parent, aq_inner
from Products.CMFCore.permissions import View, ModifyPortalContent
from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin
from Products.ATContentTypes.content.folder import ATFolder, ATBTreeFolder
from Products.Archetypes import atapi

import pmr2.mercurial
import pmr2.mercurial.utils

from pmr2.app.interfaces import *
from pmr2.app.browser.interfaces import IPublishTraverse


class SandboxContainer(ATBTreeFolder):
    """\
    Container for sandboxes in PMR2.
    """

    interface.implements(ISandboxContainer, IPMR2GetPath,)
    security = ClassSecurityInfo()

    def __init__(self, oid='sandbox', **kwargs):
        super(SandboxContainer, self).__init__(oid, **kwargs)

    security.declareProtected(View, 'get_path')
    def get_path(self):
        """See ISandboxContainer"""

        obj = aq_inner(self)
        # aq_inner needed to get out of form wrappers
        while obj is not None:
            obj = aq_parent(obj)
            if IPMR2.providedBy(obj):
                if not obj.repo_root:
                    # [1] it may be dangerous to fall through to the 
                    # next object, so we are done.
                    break
                # XXX magic string
                return os.path.join(obj.repo_root, 'sandbox')
        raise PathLookupError('repo root is undefined')

atapi.registerType(SandboxContainer, 'pmr2.app')


class Sandbox(BrowserDefaultMixin, atapi.BaseContent):
    """\
    PMR2 Sandbox object is an editable instance of the workspace.
    """

    interface.implements(ISandbox, IPMR2GetPath,)
    security = ClassSecurityInfo()

    description = fieldproperty.FieldProperty(ISandbox['description'])
    status = fieldproperty.FieldProperty(ISandbox['status'])

    security.declareProtected(View, 'get_path')
    def get_path(self):
        """See ISandbox"""

        obj = aq_inner(self)
        while obj is not None:
            obj = aq_parent(obj)
            if IPMR2GetPath.providedBy(obj):
                p = obj.get_path()
                if not p:
                    # see [1]
                    break
                return os.path.join(p, self.id)
        raise PathLookupError('parent of sandbox cannot calculate path')

atapi.registerType(Sandbox, 'pmr2.app')
