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
from pmr2.app.util import get_path


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

        # XXX magic string 'sandbox'
        result = get_path(self, 'sandbox')
        if result is None:
            raise PathLookupError('repo root is undefined')
        return result


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

        result = get_path(self, self.id) #XXX
        if result is None:
            raise PathLookupError('parent of sandbox cannot calculate path')
        return result


atapi.registerType(Sandbox, 'pmr2.app')
