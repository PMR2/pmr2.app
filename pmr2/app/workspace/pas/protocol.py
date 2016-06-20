import zope.component

from Products.PluggableAuthService.plugins.BasePlugin import BasePlugin
from AccessControl.class_init import InitializeClass
from AccessControl.SecurityInfo import ClassSecurityInfo
from Products.PluggableAuthService.utils import classImplements

from Products.PluggableAuthService.interfaces.plugins import IChallengePlugin
from Products.PluggableAuthService.plugins import HTTPBasicAuthHelper
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from pmr2.app.workspace.pas.interfaces import IStorageProtocol

# I can't be bothered adding a ZMI page to add this plugin as it should
# be completely automated.
manage_addProtocolAuthPluginForm = PageTemplateFile(
    '../zmi/addProtocolAuthPlugin',
    globals(), 
    __name__='manage_addProtocolAuthPluginForm')


def addProtocolAuthPlugin(self, id, title='', REQUEST=None):
    o = ProtocolAuthPlugin(id, title)
    self._setObject(o.getId(), o)

    if REQUEST is not None:
        REQUEST['RESPONSE'].redirect('%s/manage_main'
            '?manage_tabs_message=Protocol+PAS+Plugin+removed.' %
            self.absolute_url())

def removeProtocolAuthPlugin(self, id, title='', REQUEST=None):
    self._delObject(id)

    if REQUEST is not None:
        REQUEST['RESPONSE'].redirect('%s/manage_main'
            '?manage_tabs_message=Protocol+PAS+Plugin+removed.' %
            self.absolute_url())

class ProtocolAuthPlugin(BasePlugin):
    meta_type = 'Protocol PAS'
    security = ClassSecurityInfo()

    def __init__(self, id, title=None):
        self._setId(id)
        self.title = title

    security.declarePrivate('challenge')
    def challenge(self, request, response, **kw):
        protocols = zope.component.getUtilitiesFor(IStorageProtocol)
        result = False

        for key, protocol in protocols:
            result = protocol(request)
            if result:
                break

        if not result:
            return False

        # Couldn't inherit from HTTPBasicAuthHelper due to metaclass(?)
        # restriction(s).  Copypasta below.
        realm = response.realm
        if realm:
            response.addHeader('WWW-Authenticate',
                               'Basic realm="%s"' % realm)
        m = '<strong>You are not authorized to access this resource.</strong>'
        if response.debug_mode:
            if response._auth:
                m = m + '<p>\nUsername and password are not correct.'
            else:
                m = m + '<p>\nNo Authorization header found.'

        response.setBody(m, is_error=1)
        response.setStatus(401)
        return 1

classImplements(ProtocolAuthPlugin, IChallengePlugin)
InitializeClass(ProtocolAuthPlugin)
