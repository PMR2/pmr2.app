from os.path import splitext
from random import getrandbits

import zope.interface
import zope.component
from zope.publisher.browser import BrowserPage
from zope.i18nmessageid import MessageFactory
_ = MessageFactory("pmr2")

from paste.httpexceptions import HTTPNotFound
import z3c.form.field
from z3c.form import button
from plone.memoize.view import memoize
from plone.z3cform import layout

from Acquisition import aq_parent, aq_inner
from Products.CMFCore.utils import getToolByName
from Products.PortalTransforms.data import datastream

from pmr2.app.interfaces import *
from pmr2.app.content import *
from pmr2.app.util import *

from pmr2.app.browser.interfaces import IPublishTraverse
from pmr2.app.browser import form
from pmr2.app.browser import page
from pmr2.app.browser.page import ViewPageTemplateFile
from pmr2.app.browser import widget
from pmr2.app.browser.layout import *


class ExposureAddForm(form.AddForm):
    """\
    Exposure creation form.
    """

    fields = z3c.form.field.Fields(IExposure).select(
        'workspace',
        'commit_id',
        'curation',
    )
    fields['curation'].widgetFactory = widget.CurationWidgetFactory
    clsobj = Exposure

    def create(self, data):
        # Rely on randomly generated id, as multiple models (usually
        # different versions of same model) will use the same title
        # Tagging will be used and another search page will return
        # nice models.
        data['id'] = '%032x' % getrandbits(128)
        return form.AddForm.create(self, data)

    def add_data(self, ctxobj):
        ctxobj.workspace = self._data['workspace']
        ctxobj.commit_id = self._data['commit_id']
        ctxobj.curation = self._data['curation']
        helper = zope.component.queryAdapter(ctxobj, IExposureSourceAdapter)
        if helper:
            exposure, workspace, path = helper.source()
            ctxobj.setTitle(workspace.title)
        

ExposureAddFormView = layout.wrap_form(ExposureAddForm, 
    label="Exposure Create Form")


class ExposureEditForm(z3c.form.form.EditForm):
    """\
    Exposure editing form.
    """

    fields = z3c.form.field.Fields(IExposure).select(
        'title',
        'curation',
    )
    fields['curation'].widgetFactory = widget.CurationWidgetFactory

ExposureEditFormView = layout.wrap_form(ExposureEditForm, 
    label="Exposure Edit Form")


class ExposureEditCurationForm(z3c.form.form.EditForm):
    """\
    Exposure editing form.
    """

    fields = z3c.form.field.Fields(IExposure).select(
        'curation',
    )
    fields['curation'].widgetFactory = widget.CurationWidgetFactory

ExposureEditCurationFormView = layout.wrap_form(ExposureEditCurationForm, 
    label="Curation Editor")


class ExposureTraversalPage(page.TraversePage):
    """\
    Since any exposure page can become the root for whatever reason, we
    need to implement this in all methods.
    """

    target_view = 'rawfile'

    def portal_url(self):
        portal = getToolByName(self.context, 'portal_url').getPortalObject()
        return portal.absolute_url()

    def render(self):
        raise NotImplementedError

    def path_to_uri(self):
        helper = zope.component.queryAdapter(
            self.context, IExposureSourceAdapter)
        exposure, workspace, path = helper.source()
        filepath = '/'.join([path] + self.request['request_subpath'])
        target_uri = '%s/@@%s/%s/%s' % (workspace.absolute_url(), 
            self.target_view, exposure.commit_id, filepath)
        return target_uri

    def __call__(self, *args, **kwargs):

        if not 'request_subpath' in self.request:
            return self.render()
        target_uri = self.path_to_uri()
        return self.request.response.redirect(target_uri)


class ExposureFolderListing(ExposureTraversalPage):

    def render(self):
        # directly calling the intended python script.
        return self.context.folder_listing()


class ExposureFileGenForm(form.AddForm):
    """\
    Form to generate an exposure file (encapsulates an actual file in a
    workspace).
    """

    # Multiple choice form will need this method, but generalized.
    # This will become subclass of that.
    fields = z3c.form.field.Fields(IExposureFileGenForm)

    def create(self, data):
        self._data = data
        # XXX assert that filename exists in workspace?
        path = data['filename'].split('/')
        # get the name first
        id_ = path.pop()
        # then reverse so they will be popped in the right order
        path.reverse()

        # save this for later use.
        self._data['_path'] = path

        result = ExposureFile(id_)
        # XXX is the id validated to be not a duplicate?
        # I guess we don't need validation if the object
        self._name = result.id
        # XXX this could probably also do annotation from a list
        return result

    def resolve_folder(self, path):
        if not path:
            path = []
        if isinstance(path, basestring):
            # XXX not sure if it's "right" to make this easy/shortcut
            path = path.split('/')
        path.reverse()
        return self._resolve_folder(path)

    def _resolve_folder(self, path, create=False):
        # XXX move to separate class?
        # there are id checks for the path components within the field 
        # itself, so any failure happens (due to possible duplicates
        # invalids) will cause 
        # an exception during the nested folder creation below.

        context = self.context
        while path:
            name = path.pop()
            if name in context:
                # reusing existing context.
                context = context[name]
                if IExposureFolder.providedBy(context):
                    continue
                # we have some inconsistency, giving up.
                raise TypeError('`%s` is not an ExposureFolder' % name)

            if not create:
                # XXX exception type?
                raise ValueError('%s is not in context' % name)

            # object not exist, standard routine to create, add, reindex
            folderobj = ExposureFolder(name)
            context[name] = folderobj
            context.notifyWorkflowCreated()
            context.reindexObject()
            # done, we have next context.
            context = context[name]
        return context

    def add(self, obj):
        # switch to new context so parent class knows to here.
        # XXX other side effects from setting a new self.context?
        self.context = self._resolve_folder(self._data['_path'], True)
        # parent to add
        super(ExposureFileGenForm, self).add(obj)

    def add_data(self, ctxobj):
        # give a default title based on filename
        ctxobj.setTitle(ctxobj.id)

ExposureFileGenFormView = layout.wrap_form(ExposureFileGenForm, 
    label="Add a file to the exposure")


class ExposureFileAnnotatorForm(form.BaseAnnotationForm):
    """\
    Form to add a note to an ExposureFile.
    """

    # Multiple choice form will need this method, but generalized.
    # This will become subclass of that.
    fields = z3c.form.field.Fields(IExposureFileAnnotatorForm)

    @button.buttonAndHandler(_('Annotate'), name='apply')
    def handleAnnotate(self, action):
        self.baseAnnotate(action)

    def annotate(self):
        annotator = zope.component.getUtility(
            IExposureFileAnnotator,
            name=self._data['annotators']
        )
        annotator(self.context)()

    def nextURL(self):
        # if there are multiple choices, redirect to default view.
        # XXX default view only for now.
        note = zope.component.getAdapter(
            self.context, name=self._data['annotators'])
        if IExposureFileEditableNote.providedBy(note):
            # redirect to note editor view for the note as no data
            # should have been added.
            return '%s/@@note_editor/%s' % (self.context.absolute_url(), 
                                            self._data['annotators'])
        return '%s/@@%s' % (self.context.absolute_url(), 
                            self._data['annotators'])

ExposureFileAnnotatorFormView = layout.wrap_form(ExposureFileAnnotatorForm, 
    label="Add an annotation to an Exposure File.")


class ExposureFileNoteEditForm(form.EditForm, page.TraversePage):
    """\
    Some notes need to be user editable rather than generated.  They 
    must not be confused with the autogenerated ones, for the output may
    need sanitization that the editor cannot provide somehow (for now).

    This is the edit form for the annotation notes, it will validate
    whether the supplied annotation name provides the interface that
    allows editing.  If so, it will query for the interface with the
    fields it tracks so the correct widgets can be rendered.
    """

    zope.interface.implements(IExposureFileNoteEditForm)

    def getContent(self):
        return self.note

    def applyChanges(self, data):
        results = super(ExposureFileNoteEditForm, self).applyChanges(data)
        # since this form already assigns the data, the annotator
        # is only used to append the name of the note to the list of
        # available views.
        name = '/'.join(self.traverse_subpath)
        annotator = zope.component.getUtility(
            IExposureFileAnnotator, name=name)
        annotator(self.context)._append_view()
        return results

    def update(self):
        """\
        Since the generic call method will call this first, and the
        default update will also update the widgets and things, we will
        first update the instance with what it is supposed to be.
        """

        # fail silently on slashes, because we don't (yet) have a case 
        # where two distinct path components are needed.
        name = '/'.join(self.traverse_subpath)
        note = zope.component.queryAdapter(self.context, name=name)
        if note is None or not IExposureFileEditableNote.providedBy(note):
            # this place does not exist for notes not meant to edited.
            # or an unspecified note.
            # maybe later if note is None, we return a view that lists
            # links to the editable notes.
            raise HTTPNotFound()
        self.note = note
        # assign the field
        # XXX this appears to work, we only want the interface that is
        # directly implemented by the class, which this appears to 
        # return in the order provided.
        # See: Exposure.ExposureExport (uses same method)
        inf = zope.interface.providedBy(note).interfaces().next()
        self.fields = z3c.form.field.Fields(inf)
        super(ExposureFileNoteEditForm, self).update()

ExposureFileNoteEditFormView = layout.wrap_form(ExposureFileNoteEditForm, 
    __wrapper_class=PlainTraverseLayoutWrapper,
    label="Edit an Exposure File Note.")


class ExposureFileNoteArrangeForm(form.EditForm):
    """\
    Form to allow rearrangement of notes
    """

    #zope.interface.implements(IExposureFileNoteArrangeForm)
    fields = z3c.form.field.Fields(IExposureFile).select('views')
    fields['views'].widgetFactory = widget.TextLineListTextAreaWidgetFactory

    def update(self):
        """\
        Call update as per normal, and then filter out the resulting
        values.
        """

        result = super(ExposureFileNoteArrangeForm, self).update()
        views = [i for i in self.context.views if
                    zope.component.queryAdapter(self.context, name=i)]
        self.context.views = views
        return result

ExposureFileNoteArrangeFormView = layout.wrap_form(ExposureFileNoteArrangeForm, 
    label="Arrange Exposure File Notes.")


class ExposureDocViewGenForm(form.BaseAnnotationForm):
    """\
    Form to generate the default view of the base exposure.
    """

    # Multiple choice form will need this method, but generalized.
    # This will become subclass of that.
    ignoreContext = False
    zope.interface.implements(IExposureDocViewGenForm)
    fields = z3c.form.field.Fields(IExposureDocViewGenForm)

    def getContent(self):
        # since we are not using the same interface as the exposure
        # object as it does not use choice, to populate the values here
        # will require an adapter.
        return zope.component.getAdapter(self.context, IExposureDocViewGenForm)

    @button.buttonAndHandler(_('Generate'), name='apply')
    def handleGenerate(self, action):
        self.baseAnnotate(action)

    def annotate(self):
        if self._data['docview_gensource'] is not None:
            # XXX manual unicode call, because vocab derives data directly
            # from manifest in mercurial, which is str.
            self.context.docview_gensource = \
                unicode(self._data['docview_gensource'])
        self.context.docview_generator = self._data['docview_generator']
        if not self.context.docview_generator:
            # do nothing if we have no generator.
            return None 
        viewgen = zope.component.getUtility(
            IDocViewGen,
            name=self._data['docview_generator']
        )
        viewgen(self.context)()
        self.context.reindexObject()

    def nextURL(self):
        # return to the root, because we will only have one default view
        # that generally will work.
        return self.context.absolute_url()

ExposureDocViewGenFormView = layout.wrap_form(
    ExposureDocViewGenForm, 
    label="Generate Default View for Exposure.")


class ExposureInfo(ExposureTraversalPage):
    """\
    Inheriting from the TraversalPage because this will be the main view
    wrapping around exposure.
    """

    render = ViewPageTemplateFile('exposure_docview.pt')

    def subtitle(self):
        return self.context.Description()

    def content(self):
        return self.context.getText()

ExposureInfoView = layout.wrap_form(ExposureInfo,
    __wrapper_class=PloneviewLayoutWrapper)


class ExposureFileInfo(page.TraversePage):
    """\
    Base view of an ExposureFile object.  Shows the list of adapters.
    """

    content = ViewPageTemplateFile('exposure_file_info.pt')
    subtitle = u'Exposure File Information'

ExposureFileInfoView = layout.wrap_form(ExposureFileInfo,
    __wrapper_class=PlainLayoutWrapper)


class ExposureFileRedirectView(BrowserPage):
    """\
    This view redirects to the original file.
    """

    target_view = 'rawfile'

    def __call__(self):
        helper = zope.component.queryAdapter(
            self.context, IExposureSourceAdapter)
        exposure, workspace, path = helper.source()
        target_uri = '%s/@@%s/%s/%s' % (workspace.absolute_url(), 
            self.target_view, exposure.commit_id, path)
        return self.request.response.redirect(target_uri)


class ExposureFileViewBase(page.TraversePage):
    """\
    Base class for views that peek require the annotation adapters that
    are attached to the ExposureFile objects.
    """

    zope.interface.implements(IExposureFileView)

    @property
    def name(self):
        return self.__name__

    @property
    def view_url(self):
        return '%s/@@%s' % (self.context.absolute_url(), self.name)

    @property
    def note(self):
        # get the utility that is tailored for this view.
        return zope.component.queryAdapter(self.context, name=self.__name__)


class RawTextNote(ExposureFileViewBase):
    """\
    This is a raw text view, wrapped in a pre block by the default 
    template.
    """

    template = ViewPageTemplateFile('code.pt')
    description = u'The following is a raw text representation of the file.'
    subtitle = u'Raw text view'

    @memoize
    def content(self):
        return self.note.text

RawTextNoteView = layout.wrap_form(RawTextNote,
    __wrapper_class=PlainLayoutWrapper)


class RawContentNote(ExposureFileViewBase):
    """\
    This is a raw content view, where the raw text is rendered as a
    struture as per the default template.
    """

    template = ViewPageTemplateFile('raw_content.pt')
    description = u'The following is a raw representation of the file.'
    subtitle = u'Raw content view'

    def content(self):
        return self.note.text


class MathMLNote(RawContentNote):
    """\
    Wraps an object around the mathml view.
    """

    template = RawContentNote.content

MathMLNoteView = layout.wrap_form(MathMLNote,
    __wrapper_class=MathMLLayoutWrapper
    )


class BasicCCodeNote(RawContentNote):
    """\
    This is a raw content view, where the raw text is rendered as a
    struture as per the default template.
    """

    template = ViewPageTemplateFile('basic_ccode.pt')
    description = u'The following is a raw representation of the file.'
    subtitle = u'Raw content view'

    def content(self):
        return self.note.text

    def raw(self):
        self.request.response.setHeader('Content-Type', 'text/plain')
        return self.note.text

    def __call__(self):
        if not self.traverse_subpath:
            return super(BasicCCodeNote, self).__call__()
        elif self.traverse_subpath[0] == 'raw':
            return self.raw()
        else:
            raise HTTPNotFound()

BasicCCodeNoteView = layout.wrap_form(BasicCCodeNote,
    __wrapper_class=PlainTraverseOverridableWrapper)


class CmetaNote(ExposureFileViewBase):
    """\
    Wraps an object around the mathml view.
    """

    template = ViewPageTemplateFile('cmeta_note.pt')

CmetaNoteView = layout.wrap_form(CmetaNote, __wrapper_class=PlainLayoutWrapper)


class OpenCellSessionNoteView(ExposureFileViewBase):
    # XXX change this when we have better/generalized
    target_view = 'pcenv'

    def __call__(self):
        if self.note.filename is None:
            # no session specified.
            raise HTTPNotFound()
        helper = zope.component.queryAdapter(
            self.context, IExposureSourceAdapter)
        exposure, workspace, path = helper.source()
        target_uri = '%s/@@%s/%s/%s' % (workspace.absolute_url(), 
            self.target_view, exposure.commit_id, self.note.filename)
        return self.request.response.redirect(target_uri)


class GroupedNoteViewBase(ExposureFileViewBase):
    """\
    This view looks into a valid list of text.

    Quick way to regroup existing raw texts, or a lazy way to create new
    views but make juggling easier.

    In the future look into a clean way (and not complicated) to
    generate this.
    """

    template = ViewPageTemplateFile('sublinks.pt')
    description = u'The following is a list of available choices'
    subtitle = u'Raw text view'
    choices = {}

    @property
    def items(self):
        # XXX should this can be derived from the choices provided by 
        # context
        # the attributes/keys stored by the context plus all available
        # views could be listed (can show what can be done, what is not
        # generated)
        result = self.choices.keys()
        result.sort()
        return result

    def __call__(self):
        if not self.traverse_subpath:
            # nothing, give up early by showing the default list.
            return self.template()

        name = self.traverse_subpath[0]
        if name in self.choices:
            view = zope.component.getMultiAdapter(
                (self.context, self.request), 
                name=self.choices[name],
            )
            # since the view registered is the wrapper, we call the 
            # inner part of the it rather than itself.
            return view.form_instance()
        # XXX set an information note about invalid choice?
        return self.template()

# base
GroupedNoteViewBaseView = layout.wrap_form(
    GroupedNoteViewBase, __wrapper_class=PlainLayoutWrapper)


# utility

class ExposurePort(form.Form):
    """
    an export/importer for exposures
    """

    ignoreContext = True
    ignoreReadonly = True

    def __init__(self, *a, **kw):
        super(ExposurePort, self).__init__(*a, **kw)
        self.errors = []

    def _export(self, cur, prefix=''):

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

        # we don't have or need leading / to denote root.
        if not prefix:
            objpath = lambda x: '%s' % x
        else:
            objpath = lambda x: '%s/%s' % (prefix, x)

        # XXX this is a special case variable for ExposurePMR1Metadoc,
        # see below.
        default_fv = None

        for obj_id, obj in cur.items():
            p = objpath(obj_id)
            # do stuff depend on type

            if IExposureFile.providedBy(obj):
                # cannot use fieldvalues to automatically grab data,
                # and not needed anyway because this type only has
                # limited fields (i.e. manually exported here)
                # get list of file notes
                d = {}
                d['docview_gensource'] = obj.docview_gensource
                d['docview_generator'] = obj.docview_generator
                # now query the each views.
                d['views'] = viewinfo(obj)
                yield (p, d,)
            elif IExposureFolder.providedBy(obj):
                # we are ignorning other folder types, let an adapter
                # handle it below.
                for i in self._export(obj, p):
                    yield i
            else:
                # we don't know, so we ask an adapter to provide the
                # structure required, and trust they won't provide
                # something they don't own.
                a = zope.component.queryAdapter(obj, IExposurePortDataProvider)
                if a is not None:
                    yield a()

        # folder gets appended last for lazy reason - we assume all
        # paths will be created as files, meaning folders are created 
        # automatically, rather than creating that as file.
        # Then annotations can be assigned to them later, use viewinfo
        # to grab the relevant fields.
        fv = fieldvalues(cur)
        if default_fv:
            # XXX legacy default values
            fv.update(default_fv)
        yield (prefix, fv,)

    def export_source(self):
        return self.context

    def export(self):
        """\
        Returns a generator object that produces tuples containing the
        full path of the objects and a dictionary with values of its
        fields and annotations (notes) attached to it, along with its
        field values if applicable.
        """

        for i in self._export(self.export_source()):
            yield i

    def mold(self, target):
        """\
        Creates the new exposure at target, using what is produced by
        the export method.
        """

        for path, fields in self.export():
            if 'views' in fields:
                # XXX assume this specifies an ExposureFile
                fgen = ExposureFileGenForm(target, None)
                d = {
                    'filename': path,
                }
                fgen.createAndAdd(d)
                # XXX using something that is magic in nature
                # <form>.ctxobj is created by our customized object
                # creation method for the form, and we are using 
                # this informally declared object.
                ctxobj = fgen.ctxobj

                # generate docview
                if fields['docview_generator']:
                    ctxobj.docview_gensource = fields['docview_gensource']
                    viewgen = zope.component.getUtility(
                        IDocViewGen,
                        name=fields['docview_generator'],
                    )
                    viewgen(ctxobj)()

                for view, view_fields in fields['views']:
                    # generate views
                    annotator = zope.component.getUtility(
                        IExposureFileAnnotator,
                        name=view,
                    )
                    # pass in the view_fields regardless whether it is
                    # editable or not because editable notes will have
                    # data ignored.
                    data = view_fields and view_fields.items() or None
                    annotator(ctxobj)(data)
                ctxobj.reindexObject()
            else:
                # generate views.
                # using this to resolve the folder object
                fgen = ExposureFileGenForm(target, None)
                # XXX couldn't this just create the folder first for out
                # of order exports?
                container = fgen.resolve_folder(path)

                if fields['docview_gensource']:
                    # there is a source
                    container.docview_gensource = fields['docview_gensource']
                    viewgen = zope.component.getUtility(
                        IDocViewGen,
                        name=fields['docview_generator']
                    )
                    viewgen(container)()

                if IExposure.providedBy(container):
                    # only copy curation over, until this becomes an
                    # annotation.
                    container.curation = fields['curation']
                container.reindexObject()


class ExposurePortCommitIdForm(ExposurePort):

    # this just have commit id, create exposure.

    formErrorsMessage = _('There are errors')

    _finishedAdd = False
    fields = z3c.form.field.Fields(IExposure).select(
        'commit_id',
    )

    def find_exposure_container(self):
        context = aq_inner(self.context)
        while context:
            if IExposureContainer.providedBy(context):
                return context
            context = aq_parent(context)

    @button.buttonAndHandler(_('Migrate'), name='apply')
    def handleMigrate(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        parent = self.find_exposure_container()

        eaf = ExposureAddForm(parent, None)
        data = {
            'workspace': self.context.workspace,
            'curation': None,  # to be copied later
            'commit_id': data['commit_id'],
        }
        eaf.createAndAdd(data)
        exp_id = data['id']
        target = parent[exp_id]
        self.mold(target)
        self._finishedAdd = True
        self.target = target

    def nextURL(self):
        return self.target.absolute_url()

    def render(self):
        if self._finishedAdd:
            self.request.response.redirect(self.nextURL())
            return ""
        return super(ExposurePortCommitIdForm, self).render()

ExposurePortCommitIdFormView = layout.wrap_form(ExposurePortCommitIdForm, 
    label="Exposure Port to new commit id")

