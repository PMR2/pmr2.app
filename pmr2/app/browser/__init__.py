from zope import schema
import zope.component

from zope.app.pagetemplate import viewpagetemplatefile

from Products.ATContentTypes.content.folder import ATFolder

import z3c.form.field
import z3c.form.form

from plone.app.z3cform import layout

from pmr2.app.interfaces import *
from pmr2.app.content import *

from plone.i18n.normalizer.interfaces import IIDNormalizer


class PMR2AddForm(z3c.form.form.AddForm):
    """\
    Repository root add form.
    """

    fields = z3c.form.field.Fields(IPMR2)

    def create(self, data):
        # Object created
        id_ = data['title']
        id_ = zope.component.queryUtility(IIDNormalizer).normalize(id_)
        self._name = id_
        self._data = data

        reproot = PMR2(self._name, **data)
        return reproot

    def add(self, obj):
        # Adding object, set fields.
        self.context[self._name] = obj
        new = self.context[self._name]
        new.title = self._data['title']
        new.repo_root = self._data['repo_root']
        # XXX create dir if not exist?
        # XXX validation for the input?
        new.reindexObject()
        # create required container objects
        # XXX somehow make this part of the profile like new plone site
        # will create the default contents?
        # FIXME - less magic string
        ws_c = WorkspaceContainer('workspace')
        sb_c = SandboxContainer('sandbox')
        ex_c = ExposureContainer('exposure')
        ws_c.title = 'Workspace'
        sb_c.title = 'Sandbox'
        ex_c.title = 'Exposure'
        new['workspace'] = ws_c
        new['sandbox'] = sb_c
        new['exposure'] = ex_c
        ws_c.reindexObject()
        sb_c.reindexObject()
        ex_c.reindexObject()

    def nextURL(self):
        return "%s/%s" % (self.context.absolute_url(), self._name)

PMR2AddFormView = layout.wrap_form(PMR2AddForm, label="Repository Add Form")


class PMR2EditForm(z3c.form.form.EditForm):
    """\
    Repository Edit Form.
    """

    fields = z3c.form.field.Fields(IPMR2)

# Plone Form wrapper for the EditForm
PMR2EditFormView = layout.wrap_form(PMR2EditForm, label="Repository Edit Form")


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

