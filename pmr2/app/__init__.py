from Products.CMFPlone import interfaces as plone_interfaces
from Products import GenericSetup
from Products.CMFCore import utils as cmfutils
from Products.Archetypes import atapi
from Products.CMFCore.permissions import \
    AddPortalContent as ADD_CONTENT_PERMISSION
from Products.CMFCore.permissions import setDefaultRoles
from Products.PluggableAuthService.PluggableAuthService import \
    registerMultiPlugin


setDefaultRoles('pmr2.app: Workspace Push', ('WorkspacePusher',))


def initialize(context):
    """Initializer called when used as a Zope 2 product."""

    from pmr2.app.workspace import initialize as workspace_init
    from pmr2.app.exposure import initialize as exposure_init

    workspace_init(context)
    exposure_init(context)
