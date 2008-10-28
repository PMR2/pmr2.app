import z3c.form.field

from plone.app.z3cform import layout

from pmr2.app.interfaces import *
from pmr2.app.content import *

import form


class ExposureAddForm(form.AddForm):
    """\
    Exposure creation form.
    """

    fields = z3c.form.field.Fields(IExposure)
    clsobj = Exposure

    def add_data(self, obj):
        new.title = self._data['title']
        new.workspace = self._data['workspace']
        new.commit_id = self._data['commit_id']

ExposureAddFormView = layout.wrap_form(ExposureAddForm, label="Exposure Create Form")


class ExposureEditForm(z3c.form.form.EditForm):
    """\
    Exposure editing form.
    """

    fields = z3c.form.field.Fields(IExposure)

ExposureEditFormView = layout.wrap_form(ExposureEditForm, label="Exposure Edit Form")

