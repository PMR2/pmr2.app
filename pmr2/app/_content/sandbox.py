import os.path

from zope import interface
from zope.schema import fieldproperty
from zope.publisher.interfaces import IPublishTraverse

from AccessControl import ClassSecurityInfo
from Acquisition import aq_parent, aq_inner
from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin
from Products.ATContentTypes.content.folder import ATFolder, ATBTreeFolder
from Products.Archetypes import atapi

import pmr2.mercurial
import pmr2.mercurial.utils

from pmr2.app.interfaces import *


class SandboxContainer(ATBTreeFolder):
    """\
    Container for sandboxes in PMR2.
    """

    interface.implements(ISandboxContainer)
    security = ClassSecurityInfo()

    def __init__(self, oid='sandbox', **kwargs):
        super(SandboxContainer, self).__init__(oid, **kwargs)

    security.declareProtected(View, 'get_path')
    def get_path(self):
        """See ISandboxContainer"""

        p = aq_parent(aq_inner(self)).repo_root
        if not p:
            return None
        # XXX magic string
        return os.path.join(p, 'sandbox')

atapi.registerType(SandboxContainer, 'pmr2.app')


class Sandbox(BrowserDefaultMixin, atapi.BaseContent):
    """\
    PMR2 Sandbox object is an editable instance of the workspace.
    """

    interface.implements(ISandbox)
    security = ClassSecurityInfo()

    description = fieldproperty.FieldProperty(ISandbox['description'])
    status = fieldproperty.FieldProperty(ISandbox['status'])

    security.declareProtected(View, 'get_path')
    def get_path(self):
        """See ISandbox"""

        # aq_inner needed to get out of form wrappers
        p = aq_parent(aq_inner(self)).get_path()
        if not p:
            return None
        return os.path.join(p, self.id)

atapi.registerType(Sandbox, 'pmr2.app')
