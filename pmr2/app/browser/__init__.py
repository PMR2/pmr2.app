from zope import schema
import zope.component

from zope.app.pagetemplate import viewpagetemplatefile

from Products.ATContentTypes.content.folder import ATFolder

import z3c.form.field
import z3c.form.form

from plone.app.z3cform import layout

from pmr2.app.interfaces import *
from pmr2.app.content import RepositoryRoot

from plone.i18n.normalizer.interfaces import IIDNormalizer


class RepositoryRootAddForm(z3c.form.form.AddForm):
    """\
    Repository root add form.
    """

    fields = z3c.form.field.Fields(IRepositoryRoot)

    def create(self, data):
        # Object created
        id_ = data['title']
        id_ = zope.component.queryUtility(IIDNormalizer).normalize(id_)
        self._name = id_
        self._data = data

        reproot = RepositoryRoot(self._name, **data)
        #reproot = ATFolder(self._name, **data)
        return reproot

    def add(self, obj):
        # Adding object, set fields.
        self.context[self._name] = obj
        new = self.context[self._name]
        new.setTitle(self._data['title'])

        # XXX description duplicated?
        new.setDescription(self._data['description'])
        new.description = self._data['description']

        new.repo_root = self._data['repo_root']
        new.reindexObject()

    def nextURL(self):
        return "%s/%s" % (self.context.absolute_url(), self._name)

RepositoryRootAddFormView = layout.wrap_form(RepositoryRootAddForm, label="Repository Add Form")


class RepositoryRootEditForm(z3c.form.form.EditForm):
    """\
    Repository Edit Form.
    """

    fields = z3c.form.field.Fields(IRepositoryRoot)

# Plone Form wrapper for the EditForm
RepositoryRootEditFormView = layout.wrap_form(RepositoryRootEditForm, label="Repository Edit Form")

