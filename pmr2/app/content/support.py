from zope import interface
from zope.schema import fieldproperty

from Products.Archetypes import atapi
from Products.ATContentTypes import atct

from pmr2.app.content.interfaces import *


class PMR2Search(atct.ATBTreeFolder):
    """\
    The repository root object.
    """

    interface.implements(IPMR2Search)

    #title = fieldproperty.FieldProperty(IPMR2Search['title'])
    #description = fieldproperty.FieldProperty(IPMR2Search['description'])
    catalog_index = fieldproperty.FieldProperty(IPMR2Search['catalog_index'])

atapi.registerType(PMR2Search, 'pmr2.app')
