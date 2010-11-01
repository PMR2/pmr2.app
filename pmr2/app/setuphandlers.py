from Products.PluggableAuthService.interfaces.plugins import IChallengePlugin
from Products.PlonePAS.Extensions.Install import activatePluginInterfaces
from Products.CMFCore.utils import getToolByName
from StringIO import StringIO
from pmr2.app.pas.mercurial import addHgAuthPlugin
from pmr2.app.interfaces import IPMR2GlobalSettings
from pmr2.app.settings import PMR2GlobalSettings

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
        # activatePluginInterfaces should have done this, but it may
        # not have because something could prevent this from happening.
        uf.plugins.activatePlugin(IChallengePlugin, id_)
        print >> out, 'IChallengePlugin "%s" activated' % id_
        move_pn = activated_pn
    else:
        # Select the plugins to move down.
        move_pn = list(activated_pn)
        move_pn = move_pn[0:move_pn.index(id_)]

    # keep hgauthpas at the bottom (actually, below the cookie auth)
    # is the same as deactivating it as it will never have a chance
    # to be triggered (so manual demotion is left alone).
    uf.plugins.movePluginsDown(IChallengePlugin, move_pn)
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

def cellml_v0_2tov0_3(context):
    """Migration script specific to models.cellml.org."""

    import traceback
    from logging import getLogger

    from zope.annotation.interfaces import IAnnotations
    from pmr2.app.annotation.interfaces import IExposureFileNote
    from pmr2.app.browser.exposure import ExposureFileTypeAnnotatorForm
    from pmr2.app.adapter import ExposureSourceAdapter

    logger = getLogger('pmr2.app')
    catalog = getToolByName(context, 'portal_catalog')
    props = getToolByName(context, 'portal_properties')

    # This is the path to the ExposureFileType object defined for the
    # CellML type.  It needs to be set using the portal_properties tool.
    cellml_type = props.site_properties.getProperty('cellml_type_path')
    cellml_force = props.site_properties.getProperty('cellml_force_all')
    cellml_notes = set(['cmeta', 'basic_mathml', 'basic_ccode'])
    cellml_type_obj = cellml_type and catalog(path=cellml_type)[0].getObject()
    cellml_type_notes = cellml_type_obj and cellml_type_obj.views
    cellml_type_tags = cellml_type_obj and cellml_type_obj.tags or ()

    def migrate(context, annotations, oldnotes):
        # construct a set of old notes to verify whether or not to use
        # the CellML profile.
        oldnote_set = set(oldnotes)
        session_file = None
        if 'opencellsession' in oldnote_set:
            # It can die here because something wrong with getting the 
            # vocabulary from the manifest.
            session_file = annotations['opencellsession'].filename
            # discard this.
            oldnote_set.remove('opencellsession')

        groups = {}
        groups['opencellsession'] = [('filename', session_file),]
        if cellml_force or (cellml_type_notes and oldnote_set == cellml_notes):
            context.file_type = cellml_type
            # update views
            context.views = cellml_type_notes
            context.setSubject(cellml_type_tags)
            groups['license_citation'] = [('format', u'cellml_rdf_metadata')]
            groups['source_text'] = [('langtype', u'xml')]
        else:
            # reuse the existing views, and unknown profile.
            pass

        # annotate using the form.
        form = ExposureFileTypeAnnotatorForm(context, None)
        # It can die here too because of various reasons (workspace
        # missing, malformed input data, incompatibilities of existing
        # data with new formatting scheme, stray electrons, etc.).
        form._annotate(groups)

    files = catalog(portal_type='ExposureFile')
    for file in files:
        context = file.getObject()
        annotations = IAnnotations(context)
        oldnotes = []

        for k, v in annotations.iteritems():
            if not IExposureFileNote.providedBy(v):
                continue
            # we only want annotations created in v0.2, which is 
            # identified by the usage of non-prefixed keys.
            if k in context.views:
                oldnotes.append(k)

        if not oldnotes:
            # not doing anything since old notes are not found.
            logger.info('`%s` has no pmr2.app v0.2 styled notes to migrate.' % 
                        context.absolute_url_path())
            continue

        try:
            migrate(context, annotations, oldnotes)
        except:
            logger.error('Failed to migrate `%s` - it may be left in an '
                         'inconsistent state!' % context.absolute_url_path())
            logger.warning(traceback.format_exc())
            # naturally don't remove the old notes if we blew up.
            continue

        # remove old notes
        for k in oldnotes:
            del annotations[k]

        logger.info('`%s` had its notes migrated successfully.' % 
                    context.absolute_url_path())

