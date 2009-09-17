from os.path import splitext
from random import getrandbits

import zope.interface
import zope.component
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

ExposureAddFormView = layout.wrap_form(ExposureAddForm, label="Exposure Create Form")


class ExposureEditForm(z3c.form.form.EditForm):
    """\
    Exposure editing form.
    """

    fields = z3c.form.field.Fields(IExposure).select(
        'title',
        'curation',
    )
    fields['curation'].widgetFactory = widget.CurationWidgetFactory

ExposureEditFormView = layout.wrap_form(ExposureEditForm, label="Exposure Edit Form")


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


# also need an exposure_folder_listing that mimics the one below.

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
        self.request.response.setHeader('Content-Type', 'application/xhtml+xml')
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

    def portal_url(self):
        portal = getToolByName(self.context, 'portal_url').getPortalObject()
        return portal.absolute_url()

    @memoize
    def file_access_uris(self):
        result = []
        resolver = self.uri_resolver

        download_uri = resolver.path_to_uri(
            self.context.commit_id, self.context.origin)
        if download_uri:
            result.append({'label': u'Download', 'href': download_uri})
            run_uri = resolver.path_to_uri(
                self.context.commit_id, self.context.origin, '@@pcenv', False)
            result.append({'label': u'Solve using OpenCell', 'href': run_uri})

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
