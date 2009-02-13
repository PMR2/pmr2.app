from zope import interface
from zope.schema import fieldproperty

from Products.ATContentTypes.content.folder import ATFolder
from Products.Archetypes import atapi

from pmr2.app.interfaces import *


class PMR2(ATFolder):
    """\
    The repository root object.
    """

    interface.implements(IPMR2)

    # title is defined by ATFolder
    repo_root = fieldproperty.FieldProperty(IPMR2['repo_root'])

atapi.registerType(PMR2, 'pmr2.app')
