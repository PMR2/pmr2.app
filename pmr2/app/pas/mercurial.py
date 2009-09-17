from Products.PluggableAuthService.plugins.BasePlugin import BasePlugin
from AccessControl.SecurityInfo import ClassSecurityInfo
from Products.PluggableAuthService.utils import classImplements
from Globals import InitializeClass

from Products.PluggableAuthService.interfaces.plugins import IChallengePlugin
from Products.PluggableAuthService.plugins import HTTPBasicAuthHelper
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from pmr2.app.pas.interfaces import IHgProtocolRequest

# I can't be bothered adding a ZMI page to add this plugin as it should
# be completely automated.
#manage_addHgAuthPluginForm = PageTemplateFile('../zmi/addHgAuthPlugin',
#    globals(), __name__='manage_addHgAuthPluginForm')


def addHgAuthPlugin(self, id, title='', REQUEST=None):
    o = HgAuthPlugin(id, title)
    self._setObject(o.getId(), o)

    if REQUEST is not None:
        REQUEST['RESPONSE'].redirect('%s/manage_main'
            '?manage_tabs_message=HgAuth+PAS+Plugin+added.' %
            self.absolute_url())

def hgSniffer(request):
    return request.environ['HTTP_ACCEPT'].startswith('application/mercurial-')

# XXX we could be doing this, but I am not sure if we need to hook into
# protocol sniffer.  Hard-coding below works, for now.
#registerSniffer(IHgProtocolRequest, hgSniffer)

class HgAuthPlugin(BasePlugin):
    meta_type = 'HgAuth PAS'
    security = ClassSecurityInfo()

    def __init__(self, id, title=None):
        self._setId(id)
        self.title = title

    security.declarePrivate('challenge')
    def challenge(self, request, response, **kw):
        # This is only available to the mercurial protocol.
        if not hgSniffer(request):
            return False

        # Couldn't inherit from HTTPBasicAuthHelper due to metaclass(?)
        # restriction(s).  Copypasta below.
        realm = response.realm
        if realm:
            response.addHeader('WWW-Authenticate',
                               'basic realm="%s"' % realm)
        m = '<strong>You are not authorized to access this resource.</strong>'
        if response.debug_mode:
            if response._auth:
                m = m + '<p>\nUsername and password are not correct.'
            else:
                m = m + '<p>\nNo Authorization header found.'

        response.setBody(m, is_error=1)
        response.setStatus(401)
        return 1

classImplements(HgAuthPlugin, IChallengePlugin)
InitializeClass(HgAuthPlugin)
