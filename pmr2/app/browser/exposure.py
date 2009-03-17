from random import getrandbits

import zope.interface
import zope.app.pagetemplate.viewpagetemplatefile
from zope.publisher.interfaces import IPublishTraverse, NotFound
import z3c.form.field
from plone.app.z3cform import layout

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
        # XXX there probably should be check for existence of item with the
        # same name.
        result = ExposureDocGenerator(data)
        self._name = result.id
        return result

    def add_data(self, ctxobj):
        ctxobj.generate_content(self._data)

    # XXX this needs to create a Plone Document with the files.

ExposureDocGenFormView = layout.wrap_form(ExposureDocGenForm, label="Exposure Documentation Generation Form")


# also need an exposure_folder_listing that mimics the one below.

class ExposureFolderListing(
    page.TraversePage,
    mixin.PMR2MercurialPropertyMixin,
):

    def __call__(self, *args, **kwargs):
        if 'request_subpath' in self.request:
            filepath = '/'.join(self.request['request_subpath'])
            return self.redirect_to_file(filepath)
        else:
            # directly calling the intended python script.
            return self.context.folder_listing()

    @property
    def rev(self):
        return self.context.commit_id

    @property
    def path(self):
        return '/'.join(self.request['request_subpath'])

    def redirect_to_file(self, filepath):
        if self.fileinfo is None:
            raise NotFound(self.context, filepath, self.request)
        redir_to = '/'.join([
            self.context.get_pmr2_container().absolute_url(),
            'workspace',  # XXX magic!  should have method to return url
            self.context.workspace,
            '@@rawfile',
            self.context.commit_id,
            filepath,
        ])
        return self.request.response.redirect(redir_to)


class ExposureDocumentView(page.TraversePage):

    def __call__(self, *args, **kwargs):
        if 'request_subpath' in self.request:
            print 'doc: %s' % self.request['request_subpath']
            #import pdb;pdb.set_trace()
        else:
            # directly calling the intended python script.
            return self.context.document_view()


class ExposureMathMLView(page.SimplePage):
    """\
    Returns the MathML
    """

    def __call__(self, *args, **kwargs):
        self.request.response.setHeader('Content-Type', 'text/xml')
        return self.context.mathml


class ExposureMathMLWrapper(page.SimplePage):
    """\
    Wraps an object around the mathml view.
    """

    def __call__(self, *args, **kwargs):
        # XXX magic string
        return '<object style="width: 100%%;height:25em;" data="%s/@@view_mathml"></object>' % self.context.absolute_url()
        # XXX FIXME XSS flaw!  disabled until a better way to allow
        # editable introduction to equation is found.
        #return self.context.getRawText()

ExposureMathMLWrapperView = layout.wrap_form(ExposureMathMLWrapper)


class ExposureCmetaDocument(page.TraversePage):
    """\
    Wraps an object around the mathml view.
    """

    filetemplate = \
        zope.app.pagetemplate.viewpagetemplatefile.ViewPageTemplateFile(
        'cmeta.pt')

    def __call__(self, *args, **kwargs):
        return self.filetemplate()

ExposureCmetaDocumentView = layout.wrap_form(
    ExposureCmetaDocument,
    __wrapper_class=page.BorderedTraverseFormWrapper,
)
