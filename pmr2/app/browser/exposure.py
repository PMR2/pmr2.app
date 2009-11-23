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
        'title',
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
        ctxobj.title = self._data['title']
        ctxobj.workspace = self._data['workspace']
        ctxobj.commit_id = self._data['commit_id']
        ctxobj.curation = self._data['curation']

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


class ExposureDocGenForm(form.AddForm):
    """\
    Form to allow the generation of documentation.
    """

    # XXX main index page needs to have a brief overview of the RDF
    # metadata and citation.

    fields = z3c.form.field.Fields(IExposureDocGen)

    def create(self, data):
        # XXX could update parent item to contain/render this info
        self._data = data
        factory = zope.component.queryUtility(IExposureDocumentFactory,
                                              name=data['exposure_factory'])
        result = factory(data['filename'])
        # XXX there probably should be check for existence of item with the
        # same name somewhere else.
        self._name = result.id
        return result

    def add_data(self, ctxobj):
        ctxobj.generate_content()

    # XXX this needs to create a Plone Document with the files.

ExposureDocGenFormView = layout.wrap_form(ExposureDocGenForm, label="Exposure Documentation Generation Form")


class ExposureMetadocGenForm(form.AddForm):
    """\
    Form to allow the generation of documentation.
    """

    # XXX main index page needs to have a brief overview of the RDF
    # metadata and citation.

    fields = z3c.form.field.Fields(IExposureMetadocGen)
    notice = ViewPageTemplateFile('metadoc_notice.pt')

    def create(self, data):
        # XXX could update parent item to contain/render this info
        self._data = data
        factory = zope.component.queryUtility(IExposureMetadocFactory,
                                              name=data['exposure_factory'])
        # XXX error check make sure factory is created
        result = factory(data['filename'])
        # XXX there probably should be check for existence of item with the
        # same name somewhere else.
        self._name = result.id
        return result

    def add_data(self, ctxobj):
        if self.context.getDefaultPage() is None:
            self.context.setDefaultPage(self._name)
        ctxobj.generate_content()

    def __call__(self):
        return self.notice() + super(ExposureMetadocGenForm, self).__call__()

    # XXX this needs to create a Plone Document with the files.

ExposureMetadocGenFormView = layout.wrap_form(ExposureMetadocGenForm, label="Exposure Meta Documentation Generation Form")


class ExposureTraversalPage(page.TraversePage):
    """\
    Since any exposure page can become the root for whatever reason, we
    need to implement this in all methods.
    """

    @property
    def workspace(self):
        context = aq_inner(self.context)
        while context is not None:
            obj = zope.component.queryMultiAdapter(
                (context,), 
                name='ExposureToWorkspace',
            )
            if obj is not None:
                return obj
            context = aq_parent(context)

    @property
    def storage(self):
        """
        Updates the local values.
        """

        if not hasattr(self, '_storage'):
            self._storage = zope.component.queryMultiAdapter(
                (self.workspace, self.request, self),
                name="PMR2StorageRequestView"
            )
        return self._storage

    @property
    def uri_resolver(self):
        if not hasattr(self, '_uri_resolver'):
            self._uri_resolver = zope.component.queryMultiAdapter(
                (self.workspace,),
                name="PMR2StorageURIResolver"
            )
        return self._uri_resolver

    def portal_url(self):
        portal = getToolByName(self.context, 'portal_url').getPortalObject()
        return portal.absolute_url()

    def redirect_to_uri(self, filepath):
        redir_uri = self.uri_resolver.path_to_uri(
            self.context.commit_id, filepath)
        if redir_uri is None:
            raise HTTPNotFound(filepath)
        return self.request.response.redirect(redir_uri)

    def render(self):
        raise NotImplementedError

    def __call__(self, *args, **kwargs):

        if 'request_subpath' in self.request:
            filepath = '/'.join(self.request['request_subpath'])
            return self.redirect_to_uri(filepath)
        return self.render()


class ExposureFolderListing(ExposureTraversalPage):

    def render(self):
        # directly calling the intended python script.
        return self.context.folder_listing()


class ExposureDocumentView(ExposureTraversalPage):

    def render(self):
        return self.context.document_view()


class ExposureMathMLWrapper(ExposureTraversalPage):
    """\
    Wraps an object around the mathml view.
    """

    def render(self):
        return self.context.mathml

ExposureMathMLWrapperView = layout.wrap_form(ExposureMathMLWrapper,
    __wrapper_class=MathMLLayoutWrapper)


class ExposureRawCodeView(ExposureTraversalPage):
    """\
    Returns the raw code.
    """

    def render(self):
        self.request.response.setHeader('Content-Type', 'text/plain')
        self.request.response.setHeader('Content-Disposition', 
            'attachment; filename="%s"' % self.context.getId())
        return self.context.raw_code


class ExposureCodeWrapper(ExposureTraversalPage):
    """\
    Renders code.  Can't have wicked mangle the double brackets into
    links.
    """

    render = ViewPageTemplateFile('code.pt')
    description = u'The following is the code generated by the CellML API ' \
                   'from the CellML.'

    @memoize
    def content(self):
        return self.context.raw_code

ExposureCodeWrapperView = layout.wrap_form(
    ExposureCodeWrapper,
    __wrapper_class=BorderedTraverseFormWrapper,
)


class ExposureCmetaDocument(ExposureTraversalPage):
    """\
    Wraps an object around the mathml view.
    """

    render = ViewPageTemplateFile('cmeta.pt')

ExposureCmetaDocumentView = layout.wrap_form(ExposureCmetaDocument)


class ExposurePMR1Metadoc(ExposureTraversalPage):
    """\
    Wraps an object around the mathml view.
    """

    render = ViewPageTemplateFile('pmr1_metadoc.pt')

    @memoize
    def file_access_uris(self):
        result = []
        resolver = self.uri_resolver

        download_uri = resolver.path_to_uri(
            self.context.commit_id, self.context.origin)
        if download_uri:
            result.append({'label': u'Download CellML File', 
                'href': download_uri})
            run_uri = resolver.path_to_uri(
                self.context.commit_id, self.context.origin, '@@pcenv', False)
            result.append({'label': u'Solve using OpenCell', 'href': run_uri})

        # using resolver to "resolve" a gzip download path.
        archive_uri = resolver.path_to_uri(
            self.context.commit_id, 'gz', '@@archive', False)
        result.append({'label': u'Download (tgz)', 'href': archive_uri})

        # since session files were renamed into predictable patterns, we
        # can guess here.
        session_path = splitext(self.context.origin)[0] + '.session.xml'
        s_uri = resolver.path_to_uri(
            self.context.commit_id, session_path, '@@pcenv')
        if s_uri:
            result.append({'label': u'Solve using OpenCell Session File', 
                           'href': s_uri})
        return result

    @memoize
    def derive_from_uri(self):
        resolver = self.uri_resolver
        workspace_uri = resolver.path_to_uri(self.context.commit_id)
        manifest_uri = resolver.path_to_uri(
            self.context.commit_id, '', '@@file', False)
        result = {
            'workspace': {
                'label': self.workspace.Title,
                'href': workspace_uri,
            },
            'manifest': {
                'label': short(self.context.commit_id),
                'href': manifest_uri,
            },
        }
        return result

ExposurePMR1MetadocView = layout.wrap_form(ExposurePMR1Metadoc,
    __wrapper_class=PlainLayoutWrapper)


# v0.2 ExposureFile

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

    def add(self, obj):
        # there are id checks for the path components within the field 
        # itself, so any failure happens (due to possible duplicates
        # invalids) will cause 
        # an exception during the nested folder creation below.
        path = self._data['_path']
        context = self.context
        while path:
            name = path.pop()
            if name in context:
                # reusing existing context.
                context = context[name]
                if IExposureFolder.providedBy(context):
                    continue
                # we have some inconsistency, giving up.
                raise TypeError('%s is not an ExposureFolder', context)

            # object not exist, standard routine to create, add, reindex
            folderobj = ExposureFolder(name)
            context[name] = folderobj
            context.notifyWorkflowCreated()
            context.reindexObject()

            # done, we have next context.
            context = context[name]

        # switch to new context so parent class knows to here.
        # XXX other side effects from setting a new self.context?
        self.context = context
        # parent to add
        super(ExposureFileGenForm, self).add(obj)

    def add_data(self, ctxobj):
        # nothing to add.
        pass

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
        annotator(self.context)

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
    

class ExposureFileDocViewGenForm(form.BaseAnnotationForm):
    """\
    Form to generate all the default view of a file within an exposure.
    """

    # Multiple choice form will need this method, but generalized.
    # This will become subclass of that.
    zope.interface.implements(IExposureFileDocViewGenForm)
    fields = z3c.form.field.Fields(IExposureFileDocViewGenForm)

    @button.buttonAndHandler(_('Generate'), name='apply')
    def handleGenerate(self, action):
        self.baseAnnotate(action)

    def annotate(self):
        viewgen = zope.component.getUtility(
            IDocViewGen,
            name=self._data['docview_generator']
        )
        viewgen(self.context)

    def nextURL(self):
        # if there are multiple choices, redirect to a view.
        # XXX default view only for now.
        #return '%s/@@%s' % (self.context.absolute_url(), 
        #                    self._data['docview_generator'])
        return '%s/%s' % (self.context.absolute_url(), 'view')

ExposureFileDocViewGenFormView = layout.wrap_form(
    ExposureFileDocViewGenForm, 
    label="Generate Default View for Exposure File.")


class ExposureDocViewGenForm(form.BaseAnnotationForm):
    """\
    Form to generate the default view of the base exposure.
    """

    # Multiple choice form will need this method, but generalized.
    # This will become subclass of that.
    zope.interface.implements(IExposureDocViewGenForm)
    fields = z3c.form.field.Fields(IExposureDocViewGenForm)

    @button.buttonAndHandler(_('Generate'), name='apply')
    def handleGenerate(self, action):
        self.baseAnnotate(action)

    def annotate(self):
        # XXX Assigning the filename here because it is specified, and
        # the annotator expects a filename due to special case for
        # Exposure, and to kep the default annotator simple.
        # XXX manual unicode call
        self.context.docview_gensource = unicode(self._data['filename'])
        viewgen = zope.component.getUtility(
            IDocViewGen,
            name=self._data['docview_generator']
        )
        viewgen(self.context)

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
