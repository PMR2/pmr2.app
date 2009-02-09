from random import getrandbits

import z3c.form.field
from plone.app.z3cform import layout

from Products.ATContentTypes.content.document import ATDocument
from Products.CMFCore.utils import getToolByName
from Products.PortalTransforms.data import datastream

from pmr2.app.interfaces import *
from pmr2.app.content import *

import form


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

    fields = z3c.form.field.Fields(IExposureDocGen)

    def create(self, data):
        # XXX no check for existence of previously created item.
        self._data = data
        self._name = 'index_html'
        return ATDocument(oid=self._name)

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

