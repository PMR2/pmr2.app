from zope import interface
from zope.schema import fieldproperty

from plone.app.content import container

from Products.CMFCore.PortalFolder import PortalFolderBase
from Products.CMFDefault.DublinCore import DefaultDublinCoreImpl

from pmr2.app.interfaces import *

from Products.ATContentTypes.content.folder import ATFolder

#class RepositoryRoot(container.Container):
class RepositoryRoot(ATFolder):
    """\
    The repository root object.
    """

    interface.implements(IRepositoryRoot)

    # title is defined by ATFolder
    # description is defined by ATFolder
    repo_root = fieldproperty.FieldProperty(IRepositoryRoot['repo_root'])
