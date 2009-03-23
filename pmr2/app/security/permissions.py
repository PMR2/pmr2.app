rom Products.CMFCore.permissions import setDefaultRoles
from AccessControl import ModuleSecurityInfo

security = ModuleSecurityInfo("pmr2.app.security.permissions")

# Control the individual roles
security.declarePublic("DelegateMercurialPusherRole")
DelegateMercurialPusherRole = "Sharing page: Delegate Reader role"
setDefaultRoles(DelegateMercurialPusherRole, ('Manager', 'Owner'))
