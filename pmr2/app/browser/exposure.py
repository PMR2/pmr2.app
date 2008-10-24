import zope.component

import z3c.form.field
import z3c.form.form

from plone.app.z3cform import layout

from pmr2.app.interfaces import *
from pmr2.app.content import *

from plone.i18n.normalizer.interfaces import IIDNormalizer


class ExposureAddForm(z3c.form.form.AddForm):
    """\
    Exposure creation form.
    """

    fields = z3c.form.field.Fields(IExposure)

    def create(self, data):
        # Object created
        id_ = data['title']
        id_ = zope.component.queryUtility(IIDNormalizer).normalize(id_)
        self._name = id_
        self._data = data

        reproot = Exposure(self._name, **data)
        return reproot

    def add(self, obj):
        # Adding object, set fields.
        self.context[self._name] = obj
        new = self.context[self._name]
        new.title = self._data['title']
        new.workspace = self._data['workspace']
        new.commit_id = self._data['commit_id']
        new.reindexObject()

    def nextURL(self):
        return "%s/%s" % (self.context.absolute_url(), self._name)

ExposureAddFormView = layout.wrap_form(ExposureAddForm, label="Exposure Create Form")


class ExposureEditForm(z3c.form.form.EditForm):
    """\
    Exposure editing form.
    """

    fields = z3c.form.field.Fields(IExposure)

ExposureEditFormView = layout.wrap_form(ExposureEditForm, label="Exposure Edit Form")

