from Products.CMFPlone import interfaces as plone_interfaces
from Products import GenericSetup
from Products.CMFCore import utils as cmfutils
from Products.Archetypes import atapi
from Products.CMFCore.permissions import \
    AddPortalContent as ADD_CONTENT_PERMISSION
from Products.PluggableAuthService.PluggableAuthService import \
    registerMultiPlugin


def initialize(context):
    """Initializer called when used as a Zope 2 product."""

    #from pmr2.app.workspace import content
    from pmr2.app.workspace.pas import protocol

    content_types, constructors, ftis = atapi.process_types(
        atapi.listTypes('pmr2.app.workspace'), 'pmr2.app.workspace')

    cmfutils.ContentInit(
        'pmr2.app.workspace Content',
        content_types = content_types,
        permission = ADD_CONTENT_PERMISSION,
        extra_constructors = constructors,
        fti = ftis,
        ).initialize(context)

    registerMultiPlugin(protocol.ProtocolAuthPlugin.meta_type)

    context.registerClass(
        protocol.ProtocolAuthPlugin,
        constructors = (
            #protocol.manage_addProtocolAuthPluginForm,
            protocol.addProtocolAuthPlugin,
        ),
        visibility = None
    )
