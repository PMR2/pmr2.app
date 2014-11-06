import zope.interface
import zope.component
from zope.component.hooks import getSite
from zope.schema.interfaces import RequiredMissing

import z3c.form.interfaces

from AccessControl import getSecurityManager, Unauthorized
from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage

from pmr2.idgen.interfaces import IIdGenerator
from pmr2.app.interfaces.exceptions import ProcessingError
from pmr2.app.annotation.interfaces import IExposureFileEditableNote
from pmr2.app.annotation.interfaces import IDocViewGen, IExposureFileAnnotator

from pmr2.app.settings.interfaces import IPMR2GlobalSettings

from pmr2.app.exposure.interfaces import IExposure, IExposureFile


__all__ = [
    'fieldvalues',
    'viewinfo',
    'restrictedGetExposureContainer',
    'getExposureFileType',
    'getGenerator',
    'moldExposure',
]

def fieldvalues(obj):
    inf = zope.interface.providedBy(obj).interfaces().next()
    # XXX no error notification on missing fields.
    return dict([(fn, getattr(obj, fn, None)) for fn in inf.names()])

def viewinfo(obj):
    # maybe make this into generator in the future.
    v = []
    for vname in obj.views:
        note = zope.component.queryAdapter(obj, name=vname)
        if not note:
            # We can't export this
            # do we need error reporting? the actual page
            # is probably broken...
            continue
        if not IExposureFileEditableNote.providedBy(note):
            # assuming standard note, just get none.
            v.append((vname, None,))
            continue
        # this should be editable, grab the fields, build
        # dictionary.
        # XXX see: ExposureFileNoteEditForm

        v.append((vname, fieldvalues(note),))
    return v

def restrictedGetExposureContainer():
    # If there is a way to "magically" anchor this form at the
    # target exposure container rather than the workspace, this
    # would be unnecesary.
    settings = zope.component.queryUtility(IPMR2GlobalSettings)
    site = getSite()
    exposure_container = site.restrictedTraverse(
        str(settings.default_exposure_subpath), None)
    if exposure_container is None:
        # assume lack of permission.
        raise Unauthorized('No permission to make exposures.')
    security = getSecurityManager()
    if not security.checkPermission(permissions.AddPortalContent, 
            exposure_container):
        raise Unauthorized('No permission to make exposures.')
    return exposure_container

def getGenerator(form):
    # Using default id generator as specified by global settings. 
    # Will need to change this if exposure containers can specify
    # its own id generation scheme.
    settings = zope.component.queryUtility(IPMR2GlobalSettings)
    name = settings.default_exposure_idgen
    idgen = zope.component.queryUtility(IIdGenerator, name=name)
    if idgen is None:
        status = IStatusMessage(form.request)
        status.addStatusMessage(
            u'The exposure id generator `%s` cannot be found; '
            'please contact site administrator.' % name, 'error')
        raise z3c.form.interfaces.ActionExecutionError(
            ExposureIdGeneratorMissingError())
    return idgen

def extractError(form):
    # recursively call extractData and return a list of all errors.
    result = []
    data, errors = form.extractData()
    result.extend(errors)
    for g in form.groups:
        result.extend(extractError(g))
    return result

def getExposureFileType(form, eftype_path):
    if eftype_path is None:
        # assume default.
        return (
            '<default>',
            ['docgen'],
            (),
            None,
        )

    catalog = getToolByName(form.context, 'portal_catalog')
    if not catalog:
        # Essentially null return.
        return None

    results = catalog(
        portal_type='ExposureFileType',
        review_state='published',
        path=eftype_path,
    )
    if results:
        # there should be only one result at a specific path.
        return (
            results[0].Title,
            results[0].pmr2_eftype_views,
            results[0].pmr2_eftype_tags,
            results[0].pmr2_eftype_select_view,
        )

    # default answer.
    return (None, None, None, None)

def _mold_views(ctxobj, request, fields):
    views = []
    for view, view_fields in fields['views']:
        # generate views
        annotatorFactory = zope.component.getUtility(
            IExposureFileAnnotator,
            name=view,
        )
        # pass in the view_fields regardless whether it is
        # editable or not because editable notes will have
        # data ignored.
        data = view_fields and view_fields.items() or None
        try:
            # Annotator factory can expect request to be
            # present.  Refer to commit d5d308226767
            annotator = annotatorFactory(ctxobj, request)
            annotator(data)
            views.append(view)
        except RequiredMissing:
            # this does not cover cases where schema have
            # changed, or the old scheme into the new scheme.
            note = zope.component.queryAdapter(
                ctxobj,
                name=view
            )
            if note:
                # This editable note is missing some data,
                # probably because it never existed, bad
                # export data, updated schema or other
                # errors.  We ignore it for now, and purge
                # the stillborn note from the new object.
                del_note(ctxobj, view)
            else:
                # However, the automatic generated ones we
                # will continue to raise errors.  Maybe in
                # the future we group these together, or
                # make some way to adapt this to something
                # that will handle the migration case.
                raise
        except Exception, err:
            # XXX trap all here.
            raise ProcessingError(str(err))
    return views

def moldExposure(exposure_context, request, exported):
    """\
    Mold an exposure structure at the exposure context, using the 
    structure provided by the exported dictionary.
    """

    def caststr(s):
        # as the exported structure could be a json structure, according
        # to that spec, all strings will be in unicode, however some of
        # the internal types have been defined to be of type str.  This
        # method provides a way to properly cast them, maybe extended to
        # provide the correct encoding while retaining undefined types
        # (such as null/None).

        if not isinstance(s, basestring):
            return s
        # XXX forced casting for now
        return str(s)

    for items in exported:
        if len(items) != 2:
            raise ProcessingError('Invalid entry')

        path, fields = items
        if path is None:
            # due to wizard.
            continue

        path = caststr(path)
        # We will be calling methods that modify internal states of that
        # form, so we will require fresh instances for every file.
        fgen = zope.component.getMultiAdapter(
            (exposure_context, request), name='filegen')

        if 'views' in fields:
            # since we may use this in a regenerative context, check
            # whether file had been created.
            try:
                ctxobj = fgen.resolve_file(path)
            except ValueError:
                # I guess not.
                d = {
                    'filename': path,
                }
                fgen.createAndAdd(d)
                # XXX using something that is magic in nature
                # <form>.ctxobj is created by our customized object
                # creation method for the form, and we are using 
                # this informally declared object.
                ctxobj = fgen.ctxobj

            views = _mold_views(ctxobj, request, fields)

            # only ExposureFiles have this
            if IExposureFile.providedBy(ctxobj):
                # The annotator handles the appending of the view to the
                # final list of views that are to be made visible, but
                # it does not care about the order.  This corrects the
                # order based on the order we append it here.
                views = [view for view in views if view in ctxobj.views]
                ctxobj.views = views
                ctxobj.selected_view = fields['selected_view']
                ctxobj.file_type = caststr(fields['file_type'])
                ctxobj.setSubject(fields['Subject'])

            ctxobj.reindexObject()
        else:

            # XXX couldn't this just create the folder first for out
            # of order exports?
            container = fgen.resolve_folder(path)

            if fields['docview_gensource']:
                # there is a source
                # XXX I have unicode/str confusion
                gensource = unicode(fields['docview_gensource'])
                container.docview_gensource = gensource
                viewgen = zope.component.queryUtility(
                    IDocViewGen,
                    name=fields['docview_generator']
                )
                if viewgen:
                    # and the view generator is still available
                    try:
                        viewgen(container)()
                    except Exception, err:
                        # XXX trap all here.
                        raise ProcessingError(str(err))

            if IExposure.providedBy(container):
                # only copy curation over, until this becomes an
                # annotation.
                container.curation = fields['curation']
            container.setSubject(fields['Subject'])
            container.reindexObject()

