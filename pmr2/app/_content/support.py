from zope import interface
from zope.schema import fieldproperty

from Products.Archetypes import atapi
from Products.ATContentTypes import atct

from pmr2.app.interfaces import *
from pmr2.app.mixin import TraversalCatchAll


class PMR2Search(atct.ATBTreeFolder, TraversalCatchAll):
    """\
    The repository root object.
    """

    interface.implements(IPMR2Search)

    title = fieldproperty.FieldProperty(IPMR2Search['title'])
    description = fieldproperty.FieldProperty(IPMR2Search['description'])
    catalog_index = fieldproperty.FieldProperty(IPMR2Search['catalog_index'])

    def __before_publishing_traverse__(self, ob, request):
        TraversalCatchAll.__before_publishing_traverse__(self, ob, request)
        atct.ATBTreeFolder.__before_publishing_traverse__(self, ob, request)

atapi.registerType(PMR2Search, 'pmr2.app')
