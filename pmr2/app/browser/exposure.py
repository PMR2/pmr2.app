from random import getrandbits

import zope.interface
import zope.component
import zope.app.pagetemplate.viewpagetemplatefile
from zope.publisher.interfaces import IPublishTraverse, NotFound
import z3c.form.field
from plone.z3cform import layout

from Products.CMFCore.utils import getToolByName
from Products.PortalTransforms.data import datastream

from pmr2.app.interfaces import *
from pmr2.app.content import *
from pmr2.app.util import *

import form
import page
import mixin
import widget


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
    notice = zope.app.pagetemplate.viewpagetemplatefile.ViewPageTemplateFile(
        'metadoc_notice.pt')

    def create(self, data):
        # XXX could update parent item to contain/render this info
        self._data = data
        factory = zope.component.queryUtility(IExposureMetadocFactory,
                                              name=data['exposure_factory'])
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

class ExposureTraversalPage(
    page.TraversePage,
    mixin.PMR2MercurialPropertyMixin,
):
    """\
    Since any exposure page can become the root for whatever reason, we
    need to implement this in all methods.
    """

    @property
    def rev(self):
        return self.context.commit_id

    @property
    def path(self):
        return '/'.join(self.request['request_subpath'])

    def redirect_to_file(self, filepath):
        redir_uri = self.context.resolve_path(filepath)
        if redir_uri is None:
            raise NotFound(self.context, filepath, self.request)
        return self.request.response.redirect(redir_uri)

    def render(self):
        raise NotImplementedError

    def __call__(self, *args, **kwargs):
        if 'request_subpath' in self.request:
            filepath = '/'.join(self.request['request_subpath'])
            return self.redirect_to_file(filepath)
        return self.render()


class ExposureFolderListing(ExposureTraversalPage):

    def render(self):
        # directly calling the intended python script.
        return self.context.folder_listing()


class ExposureDocumentView(ExposureTraversalPage):

    def render(self):
        return self.context.document_view()


class ExposureMathMLView(ExposureTraversalPage):
    """\
    Returns the MathML
    """

    def render(self):
        self.request.response.setHeader('Content-Type', 'text/xml')
        return self.context.mathml


class ExposureMathMLWrapper(ExposureTraversalPage):
    """\
    Wraps an object around the mathml view.
    """

    def render(self):
        # XXX magic string
        return '<object style="width: 100%%;height:25em;" data="%s/@@view_mathml"></object>' % self.context.absolute_url()
        # XXX FIXME XSS flaw!  disabled until a better way to allow
        # editable introduction to equation is found.
        #return self.context.getRawText()

ExposureMathMLWrapperView = layout.wrap_form(ExposureMathMLWrapper)


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

    render = zope.app.pagetemplate.viewpagetemplatefile.ViewPageTemplateFile(
        'code.pt')

ExposureCodeWrapperView = layout.wrap_form(ExposureCodeWrapper)


class ExposureCmetaDocument(ExposureTraversalPage):
    """\
    Wraps an object around the mathml view.
    """

    render = zope.app.pagetemplate.viewpagetemplatefile.ViewPageTemplateFile(
        'cmeta.pt')

ExposureCmetaDocumentView = layout.wrap_form(ExposureCmetaDocument)


class ExposurePMR1Metadoc(ExposureTraversalPage):
    """\
    Wraps an object around the mathml view.
    """

    render = zope.app.pagetemplate.viewpagetemplatefile.ViewPageTemplateFile(
        'pmr1_metadoc.pt')

    def portal_url(self):
        portal = getToolByName(self.context, 'portal_url').getPortalObject()
        return portal.absolute_url()

ExposurePMR1MetadocView = layout.wrap_form(ExposurePMR1Metadoc)
