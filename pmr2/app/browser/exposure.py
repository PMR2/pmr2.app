from os.path import splitext
from random import getrandbits

import zope.interface
import zope.component
from zope.publisher.browser import BrowserPage
from paste.httpexceptions import HTTPNotFound
import z3c.form.field
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
from pmr2.app.browser.layout import PlainLayoutWrapper, MathMLLayoutWrapper, \
    BorderedTraverseFormWrapper


class ExposureAddForm(form.AddForm):
    """\
    Exposure creation form.
    """

    fields = z3c.form.field.Fields(IExposure)
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
        self.context.raw_code

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


class ExposureFileAnnotatorForm(form.AddForm):
    """\
    Form to add a note to an ExposureFile.
    """

    # Multiple choice form will need this method, but generalized.
    # This will become subclass of that.
    fields = z3c.form.field.Fields(IExposureFileAnnotatorForm)

    def create(self, data):
        self._data = data
        annotator = zope.component.getUtility(
            IExposureFileAnnotator,
            name=data['annotators']
        )
        return annotator

    def add(self, obj):
        # we don't actually add the obj into the ExposureFile, we call
        # it with the context as the argument, magic happens.
        obj.write(self.context)

    def nextURL(self):
        # we want our context to be the object that provides the URL.
        self.ctxobj = self.context
        # XXX will need to redirect to the view associated with the
        # generator somehow... just going to use default for now.
        url = form.AddForm.nextURL(self)
        return url

ExposureFileAnnotatorFormView = layout.wrap_form(ExposureFileAnnotatorForm, 
    label="Add an annotation to an Exposure File.")


class ExposureFileDocViewGenForm(form.AddForm):
    """\
    Form to generate all the required notes for the selected view.
    """

    # Multiple choice form will need this method, but generalized.
    # This will become subclass of that.
    zope.interface.implements(IExposureFileDocViewGenForm)
    fields = z3c.form.field.Fields(IExposureFileDocViewGenForm)

    def create(self, data):
        self._data = data
        view = zope.component.getUtility(
            IExposureFileDocViewGen,
            name=data['docview_generator']
        )
        return view

    def add(self, obj):
        # we don't actually add the obj into the ExposureFile, we call
        # it with the view, which then it will determine what to do
        obj(self.context)

    def nextURL(self):
        # we want our context to be the object that provides the URL.
        self.ctxobj = self.context
        # XXX will need to redirect to the view associated with the
        # generator somehow... just going to use default for now.
        url = form.AddForm.nextURL(self)
        return url

ExposureFileDocViewGenFormView = layout.wrap_form(
    ExposureFileDocViewGenForm, 
    label="Generate Default View for Exposure File.")


class PMR1ExposureFileGenForm(ExposureFileGenForm):
    """\
    Adds adapters that are part of the view.
    """

    def add_data(self, ctxobj):
        pass

ExposureDocGenFormView = layout.wrap_form(ExposureDocGenForm, 
    label="Exposure Documentation Generation Form")


class ExposureInfo(ExposureTraversalPage):
    """\
    Inheriting from the TraversalPage because this will be the main view
    wrapping around exposure.
    """

    render = ViewPageTemplateFile('exposure_info.pt')

    @memoize
    def pmr1_curation(self):
        """
        Temporary method for PMR1 compatibility styles.
        """

        pairs = (
            ('pmr_curation_star', u'Curation Status:'),
            ('pmr_pcenv_star', u'OpenCell:'),
            ('pmr_jsim_star', u'JSim:'),
            ('pmr_cor_star', u'COR:'),
        )
        curation = self.context.curation or {}
        result = []
        for key, label in pairs:
            # first item or character
            stars = key in curation and curation[key][0] or u'0'
            result.append({
                'label': label,
                'stars': stars,
            })
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

    @memoize
    def file_access_uris(self):
        result = []
        resolver = self.uri_resolver

        # using resolver to "resolve" a gzip download path.
        archive_uri = resolver.path_to_uri(
            self.context.commit_id, 'gz', '@@archive', False)
        result.append({'label': u'Download (tgz)', 'href': archive_uri})

        return result

ExposureInfoView = layout.wrap_form(ExposureInfo,
    __wrapper_class=PlainLayoutWrapper)


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
        exposure, workspace, path = self.context.source()
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
