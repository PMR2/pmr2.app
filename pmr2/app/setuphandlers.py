from Products.PluggableAuthService.interfaces.plugins import IChallengePlugin
from Products.PlonePAS.Extensions.Install import activatePluginInterfaces
from Products.CMFCore.utils import getToolByName
from StringIO import StringIO
from pmr2.app.pas.mercurial import addHgAuthPlugin
from pmr2.app.settings import IPMR2GlobalSettings, PMR2GlobalSettings

def add_pas_plugin(site):
    """Add our plugin into PAS"""

    out = StringIO()
    uf = getToolByName(site, 'acl_users')
    installed = uf.objectIds()

    id_ = 'hgauthpas'

    if id_ not in installed:
        addHgAuthPlugin(uf, id_, 'HgAuth PAS')
        activatePluginInterfaces(site, id_, out)
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

    return out.getvalue()

def add_pmr2(site):
    """Add PMR2 settings utility to the site manager"""
    out = StringIO()
    sm = site.getSiteManager()
    if not sm.queryUtility(IPMR2GlobalSettings):
        print >> out, 'PMR2 Global Settings registered'
        sm.registerUtility(IPMR2GlobalSettings(site), IPMR2GlobalSettings)
    return out.getvalue()

def remove_pmr2(site):
    """Remove PMR2 settings utility from the site manager"""
    out = StringIO()
    sm = site.getSiteManager()
    u = sm.queryUtility(IPMR2GlobalSettings)
    if u:
        print >> out, 'PMR2 Global Settings unregistered'
        sm.unregisterUtility(u, IPMR2GlobalSettings)
    return out.getvalue()

def importVarious(context):
    """Install the HgAuthPAS plugin"""

    site = context.getSite()
    print add_pas_plugin(site)
    print add_pmr2(site)
