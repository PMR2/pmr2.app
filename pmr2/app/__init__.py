from Products.CMFPlone import interfaces as plone_interfaces
from Products import GenericSetup
from Products.CMFCore import utils as cmfutils
from Products.Archetypes import atapi
from Products.CMFCore.permissions import AddPortalContent as ADD_CONTENT_PERMISSION

def initialize(context):
    """Initializer called when used as a Zope 2 product."""

    from pmr2.app import content

    content_types, constructors, ftis = atapi.process_types(atapi.listTypes('pmr2.app'), 'pmr2.app')

    cmfutils.ContentInit(
        'pmr2.app Content',
        content_types = content_types,
        permission = ADD_CONTENT_PERMISSION,
        extra_constructors = constructors,
        fti = ftis,
        ).initialize(context)

