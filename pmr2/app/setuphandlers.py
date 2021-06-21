import zope.component
from logging import getLogger

from Products.PluggableAuthService.interfaces.plugins import IChallengePlugin
from Products.PlonePAS.Extensions.Install import activatePluginInterfaces
from Products.CMFCore.utils import getToolByName
from pmr2.app.workspace.pas.protocol import addProtocolAuthPlugin
from pmr2.app.workspace.pas.protocol import removeProtocolAuthPlugin

from pmr2.app.settings.interfaces import IPMR2GlobalSettings
from pmr2.app.settings import PMR2GlobalSettings

def add_pas_plugin(site):
    """Add our plugin into PAS"""

    uf = getToolByName(site, 'acl_users')
    installed = uf.objectIds()
    logger = getLogger('pmr2.app')

    id_ = 'pmr2authpas'

    if id_ not in installed:
        addProtocolAuthPlugin(uf, id_, 'PMR2 Protocol Auth PAS')
        try:
            activatePluginInterfaces(site, id_)
        except TypeError:
            # Plone 3
            raise
            activatePluginInterfaces(site, id_, out)
    else:
        logger.info('`%s` already installed', id_)

    # check for and activate the wanted plugins
    activated_pn = uf.plugins.listPluginIds(IChallengePlugin)
    if id_ not in activated_pn:
        # activatePluginInterfaces should have done this, but it may
        # not have because something could prevent this from happening.
        uf.plugins.activatePlugin(IChallengePlugin, id_)
        logger.info('IChallengePlugin "%s" activated', id_)
        move_pn = activated_pn
    else:
        # Select the plugins to move down.
        move_pn = list(activated_pn)
        move_pn = move_pn[0:move_pn.index(id_)]

    # keep our auth at the bottom (actually, below the cookie auth)
    # is the same as deactivating it as it will never have a chance
    # to be triggered (so manual demotion is left alone).
    uf.plugins.movePluginsDown(IChallengePlugin, move_pn)
    logger.info('IChallengePlugin "%s" moved to top', id_)

def add_pmr2(site):
    """Add PMR2 settings utility to the site manager"""
    logger = getLogger('pmr2.app')
    sm = site.getSiteManager()
    if not sm.queryUtility(IPMR2GlobalSettings):
        logger.info('PMR2 Global Settings registered')
        sm.registerUtility(IPMR2GlobalSettings(site), IPMR2GlobalSettings)

def remove_pmr2(site):
    """Remove PMR2 settings utility from the site manager"""
    logger = getLogger('pmr2.app')
    sm = site.getSiteManager()
    u = sm.queryUtility(IPMR2GlobalSettings)
    if u:
        logger.info('PMR2 Global Settings unregistered')
        sm.unregisterUtility(u, IPMR2GlobalSettings)
    # XXX the actual annotation is not removed.

def reregister_pmr2_settings(site):
    """
    Re-register PMR2 due to migration.
    """
    logger = getLogger('pmr2.app')
    sm = site.getSiteManager()
    settings = sm.queryUtility(IPMR2GlobalSettings)
    if not settings:
        logger.info('Please install PMR2 first before readding the settings.')
        return
    sm.unregisterUtility(settings, IPMR2GlobalSettings)
    sm.registerUtility(settings, IPMR2GlobalSettings)
    logger.info('PMR2 Global Settings re-registered')

def importVarious(context):
    """Install the ProtocolAuthPAS plugin"""

    site = context.getSite()
    logger = getLogger('pmr2.app')
    add_pas_plugin(site)
    add_pmr2(site)

def cellml_v0_2tov0_3(context):
    """Migration script specific to models.cellml.org."""

    import traceback

    from zope.annotation.interfaces import IAnnotations
    from pmr2.app.annotation.interfaces import IExposureFileNote

    try:
        from pmr2.app.exposure.browser.browser import \
            ExposureFileTypeAnnotatorForm
    except ImportError:
        from pmr2.app.browser.exposure import ExposureFileTypeAnnotatorForm

    try:
        from pmr2.app.adapter import ExposureSourceAdapter
    except ImportError:
        from pmr2.app.exposure.adapter import ExposureSourceAdapter

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


def exposure_rand_to_seq(context):
    """\
    Migration script specific to models.cellml.org.

    This script converts the id of exposures to use sequential id, using
    the pmr2.idgen product, and move them to the new, shorter dir.
    """

    import traceback
    from pmr2.idgen.interfaces import IIdGenerator
    from zope.component.hooks import getSite

    try:
        from pmr2.app.exposure.browser import ExposureAddForm
        from pmr2.app.exposure.browser import ExposurePort
    except ImportError:
        from pmr2.app.browser.exposure import ExposureAddForm
        from pmr2.app.browser.exposure import ExposurePort

    try:
        from pmr2.app.exposure.content import Exposure
    except ImportError:
        from pmr2.app.content import Exposure

    logger = getLogger('pmr2.app')
    wft = getToolByName(context, 'portal_workflow')

    def clone(exposure, newid):
        oldid = exposure.id
        try:
            obj = exposure.getObject()
            container.manage_clone(obj, newid)
            logger.info('exposure `%s` copied to `%s`' % (oldid, newid))

            wft.doActionFor(container[newid], 'publish')
            wft.doActionFor(obj, 'expire')
            logger.info('workflow state updated')
        except:
            logger.warning(traceback.format_exc())
            logger.error('`%s` not cloned to `%s; aborted`' % (oldid, newid))
            raise

    def port(exposure, newid):
        # XXX alternative/more verbose way to get this done; mutually
        # exclusive with above method.
        oldid = exposure.id
        try:
            eaf = ExposureAddForm(container, None)
            data = {
                'workspace': exposure.pmr2_exposure_workspace,
                'curation': None,
                'commit_id': exposure.pmr2_exposure_commit_id,
            }
            eaf.createAndAdd(data)
            exp_id = data['id']
            logger.info('exposure `%s` copied to `%s`' % (oldid, newid))

            obj = exposure.getObject()
            target = container[exp_id]
            ep = ExposurePort(obj, None)
            ep.mold(target)
            logger.info('exposure `%s` ported to `%s`' % (oldid, newid))

            wft.doActionFor(obj, 'expire')
            logger.info('expired `%s`' % (oldid,))
        except:
            logger.error('failed: `%s` not ported to `%s`' % (oldid, newid))
            logger.warning(traceback.format_exc())
            raise

    props = getToolByName(context, 'portal_properties')
    old_id = props.site_properties.getProperty('exposure_old_container')
    if not old_id:
        logger.info('no old exposure id specified; nothing to do.')
        return

    site = getSite()
    u = zope.component.queryUtility(IPMR2GlobalSettings)
    old_container = u.siteManagerUnrestrictedTraverse(old_id)
    path = '/'.join(old_container.getPhysicalPath())

    catalog = getToolByName(context, 'portal_catalog')
    exposures = catalog(portal_type='Exposure', path=path,
        review_state='published', sort_on='created')

    # need the full path
    container = site.unrestrictedTraverse('/'.join(('',) + 
        u.getExposureContainer().getPhysicalPath()))

    counter = zope.component.getUtility(IIdGenerator, 'autoinc')

    for exposure in exposures:
        newid = '%x' % (counter.next())
        clone(exposure, newid)

def remove_hg_pas_plugin(site):
    """Remove Mercurial specific PAS"""

    logger = getLogger('pmr2.app')
    uf = getToolByName(site, 'acl_users')
    installed = uf.objectIds()

    id_ = 'hgauthpas'

    # check for status of our plugin, deactivate if active.
    activated_pn = uf.plugins.listPluginIds(IChallengePlugin)
    if id_ in activated_pn:
        # activatePluginInterfaces should have done this, but it may
        # not have because something could prevent this from happening.
        uf.plugins.deactivatePlugin(IChallengePlugin, id_)
        logger.info('IChallengePlugin "%s" deactivated' % id_)

    if id_ in installed:
        removeProtocolAuthPlugin(uf, id_, 'PMR2 Protocol Auth PAS')

def mercurial_storage(context):
    # In v0.4, workspace must specify its storage backend as mercurial
    # is no longer implied.  This migration script assumes this is was a
    # v0.3 instance such that it would assign mercurial to all
    # workspaces.
    from zope.component import getUtility
    from zope.schema.interfaces import IVocabularyFactory
    v = getUtility(IVocabularyFactory, name='pmr2.vocab.storage')
    tokens = v(None).by_token
    if 'mercurial' not in tokens:
        raise KeyError('mercurial not registered as a backend; '
                       'please reinstall pmr2.mercurial.')
    logger = getLogger('pmr2.app')
    catalog = getToolByName(context, 'portal_catalog')

    counter = 0
    brains = catalog(portal_type='Workspace')
    logger.info('%d workspace(s) found...' % len(brains))
    for b in brains:
        wks = b.getObject()
        if wks.storage:
            continue
        wks.storage = u'mercurial'
        counter += 1
    logger.info('%d workspace(s) with undefined storage backend is now set '
                'to use mercurial.' % counter)
    return

def fix_exposure_workspace_path(context):
    """\
    Update the Exposure workspace path to what is expected in future
    versions.
    """

    logger = getLogger('pmr2.app')
    catalog = getToolByName(context, 'portal_catalog')
    brains = catalog(portal_type='Exposure')

    settings = zope.component.queryUtility(IPMR2GlobalSettings)
    workspace_root = settings.getWorkspaceContainer().getPhysicalPath()
    # XXX weirdness with acquisition, we fix it in the case that
    # something broke.
    if workspace_root[0] != '':
        workspace_root = ('',) + workspace_root

    count = 0
    for brain in brains:
        exposure = brain.getObject()
        # update to the new format.
        if not exposure.workspace.startswith('/'):
            fp = '/'.join(workspace_root + (exposure.workspace,))
            count += 1
            exposure.workspace = fp
    logger.info('%d exposures had workspace field updated.' % count)

def filetype_bulk_update(context):
    import traceback
    import transaction

    from pmr2.app.annotation.interfaces import IExposureFileNote
    from pmr2.app.exposure.browser.util import viewinfo
    # Need to fake a request object, since the migrate step lacks one
    # for some unknown reason.
    from z3c.form.testing import TestRequest

    try:
        from pmr2.app.exposure.browser.browser import \
            ExposureFileTypeAnnotatorForm
    except ImportError:
        from pmr2.app.browser.exposure import ExposureFileTypeAnnotatorForm

    logger = getLogger('pmr2.app')
    catalog = getToolByName(context, 'portal_catalog')

    brains = catalog(portal_type='ExposureFileType')
    filetypes = dict([(b.getPath(), b.pmr2_eftype_views) for b in brains])
    if not filetypes:
        logger.error('Please reindex or create some Exposure File Types '
                     'before running this.')
        return

    errors = []
    commit_interval = 100
    files = catalog(portal_type='ExposureFile')
    t = len(files)
    for c, b in enumerate(files, 1):
        file_sp = transaction.savepoint()
        file = b.getObject()
        logger.info('Rebuilding notes for `%s` (%d/%d).',
                    file.absolute_url_path(), c, t)
        ftpath = file.file_type
        if not ftpath:
            continue

        if not ftpath in filetypes:
            # XXX only log this information for now, we may need to give
            # adminstrators some way to automatically migrate to a new
            # existing type since the old one was removed.
            logger.warning('`%s` has `%s` as its filetype but it no longer '
                           'exists ' % (file.absolute_url_path(), ftpath))
            continue

        cftviews = filetypes[ftpath]  # file type views for current file

        try:
            # assign the new set of views
            # annotate using the form.
            file.views = cftviews
            # XXX does not set the new subjects, i.e. not applying tags
            # via setSubject method of this file object
            groups = {}
            for k, v in viewinfo(file):
                groups[k] = v and v.items() or None
            # the fake request is needed for the annotator form to
            # resolve the views that are truly available, such that
            # annotations/notes that do not have a view defined are
            # automatically hidden.
            req = TestRequest()
            req.environ = {}
            form = ExposureFileTypeAnnotatorForm(file, req)
            form._annotate(groups)
            file.reindexObject()
        except:
            file_sp.rollback()
            errors.append(file.absolute_url_path())
            logger.error('Failed to rebuild `%s`' % file.absolute_url_path())
            logger.warning(traceback.format_exc())
            continue

        if c % commit_interval == 0:
            transaction.get().commit()
            logger.info('Committed transaction, interval %d reached' % 
                        commit_interval)

    if errors:
        logger.error('The following file(s) have failed to rebuild:\n%s' %
                     '\n'.join(errors))

def purge_unassigned_notes(context):
    # this indiscriminately purge all notes not found within an file's
    # specified exposure file type.
    # XXX implement an alternate option that will retain any specified
    # notes
    # XXX don't make this method available in the upgrade step just yet.
    from zope.annotation.interfaces import IAnnotations

    prefix = 'pmr2.annotation.notes-'
    catalog = getToolByName(context, 'portal_catalog')
    files = catalog(portal_type='ExposureFile')
    for b in files:
        file = b.getObject()
        ftpath = file.file_type
        if not ftpath:
            continue

        cftviews = filetypes[ftpath]  # file type views for current file

        # remove unreferenced annotations
        # XXX this assumes users don't manually assign views after
        # specifying file types.
        annotations = IAnnotations(file)
        for k in annotations.keys():
            if not k.startswith(prefix):
                continue
            viewname = k[len(prefix):]
            if not viewname in cftviews:
                del annotations[k]

def pmr2_v0_4(context):
    from zope.component.hooks import getSite
    site = getSite()
    mercurial_storage(context)
    reregister_pmr2_settings(site)
    remove_hg_pas_plugin(site)
    fix_exposure_workspace_path(site)


# v0.6

def migrate_docgen(context):
    import traceback
    from logging import getLogger
    logger = getLogger('pmr2.app.migration')
    from pmr2.app import _migration

    catalog = getToolByName(context, 'portal_catalog')
    brains = catalog(portal_type='ExposureFile')
    for b in brains:
        file = b.getObject()
        try:
            _migration.file_docgen_to_annotation(file)
        except:
            logger.error('Could not migrate docgen for %s' % b.getPath())
            logger.warning(traceback.format_exc())

    return

def pmr2_v0_6(context):
    from zope.component.hooks import getSite
    site = getSite()
    migrate_docgen(site)

def pmr2_v0_9(context):
    from zope.component.hooks import getSite
    site = getSite()
    migrate_workspace_workflow(site)

def migrate_workspace_workflow(site):
    logger = getLogger('pmr2.app')
    wft = getToolByName(site, 'portal_workflow')
    catalog = getToolByName(site, 'portal_catalog')

    action_map = {
        'pending': 'submit',
        'published': 'publish',
    }

    # get all workspaces
    workspaces = catalog(portal_type='Workspace')

    for workspace in workspaces:
        obj = workspace.getObject()
        action = action_map.get(workspace.review_state)
        if action:
            logger.debug('restoring %s to %s',
                workspace.getPath(), workspace.review_state)
            wft.doActionFor(obj, action)
