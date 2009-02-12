from random import getrandbits

import zope.interface
from zope.publisher.interfaces import IPublishTraverse
import z3c.form.field
from plone.app.z3cform import layout

from Products.CMFCore.utils import getToolByName
from Products.PortalTransforms.data import datastream

from pmr2.app.interfaces import *
from pmr2.app.content import *

import form
import page


class ExposureAddForm(form.AddForm):
    """\
    Exposure creation form.
    """

    fields = z3c.form.field.Fields(IExposure)
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

    fields = z3c.form.field.Fields(IExposure)

ExposureEditFormView = layout.wrap_form(ExposureEditForm, label="Exposure Edit Form")


class ExposureDocGenForm(form.AddForm):
    """\
    Form to allow the generation of documentation.
    """

    # XXX main index page needs to have a brief overview of the RDF
    # metadata and citation.

    fields = z3c.form.field.Fields(IExposureDocGen)

    def create(self, data):
        # XXX need to update the main index page most likely to point
        # to this documentation
        self._data = data
        # there probably should be check for existence of item with the
        # same name.
        # XXX filename extension of .html might not be desirable.
        self._name = self._data['filename'] + '.html'
        return ExposureDocument(oid=self._name)

    def add_data(self, ctxobj):
        ctxobj.setTitle(self.context.title)

        input = self.context.get_file(self._data['filename'])

        pt = getToolByName(self.context, 'portal_transforms')
        data = datastream('processor')
        pt.convert(self._data['transform_list'], input, data)

        ctxobj.setText(data.getData())
        ctxobj.setContentType('text/html')

    # XXX this needs to create a Plone Document with the files.

ExposureDocGenFormView = layout.wrap_form(ExposureDocGenForm, label="Exposure Documentation Generation Form")


# also need an exposure_folder_listing that mimics the one below.

class ExposureFolderListing(page.TraversePage):

    def __call__(self, *args, **kwargs):
        if 'request_subpath' in self.request:
            filepath = '/'.join(self.request['request_subpath'])
            return self.redirect_to_file(filepath)
        else:
            # directly calling the intended python script.
            return self.context.folder_listing()

    def redirect_to_file(self, filepath):
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

