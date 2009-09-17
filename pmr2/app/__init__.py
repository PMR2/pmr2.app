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

    from pmr2.app import content
    from pmr2.app.pas import mercurial

    content_types, constructors, ftis = atapi.process_types(atapi.listTypes('pmr2.app'), 'pmr2.app')

    cmfutils.ContentInit(
        'pmr2.app Content',
        content_types = content_types,
        permission = ADD_CONTENT_PERMISSION,
        extra_constructors = constructors,
        fti = ftis,
        ).initialize(context)

    registerMultiPlugin(mercurial.HgAuthPlugin.meta_type) # Add to PAS menu

    context.registerClass(
        mercurial.HgAuthPlugin,
        constructors = (
            #mercurial.manage_addHgAuthPluginForm,
            mercurial.addHgAuthPlugin,
        ),
        visibility = None
    )
