from Products.PluggableAuthService.interfaces.plugins import IChallengePlugin
from Products.PlonePAS.Extensions.Install import activatePluginInterfaces
from Products.CMFCore.utils import getToolByName
from StringIO import StringIO
from pmr2.app.pas.mercurial import addHgAuthPlugin

def importVarious(context):
    """Install the HgAuthPAS plugin"""
    out = StringIO()
    portal = context.getSite()

    uf = getToolByName(portal, 'acl_users')
    installed = uf.objectIds()

    id_ = 'hgauthpas'

    if id_ not in installed:
        addHgAuthPlugin(uf, id_, 'HgAuth PAS')
        activatePluginInterfaces(portal, id_, out)
    else:
        print >> out, '%s already installed' % id_

    # check for and activate the wanted plugins
    activated_pn = uf.plugins.listPluginIds(IChallengePlugin)
    if id_ not in activated_pn:
        uf.plugins.activatePlugin(IChallengePlugin, id_)
        print >> out, 'IChallengePlugin "%s" activated' % id_
        # only move our plugin to the top if we just activated it, as
        # keeping it at the bottom (actually, below the cookie auth)
        # is the same as deactivating it as it will never have a chance
        # to be triggered (so manual demotion is left alone).
        uf.plugins.movePluginsDown(IChallengePlugin, activated_pn)
        print >> out, 'IChallengePlugin "%s" moved to top' % id_

    print out.getvalue()
