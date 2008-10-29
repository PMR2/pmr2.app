import zope.component

import z3c.form.field
import z3c.form.form

from plone.app.z3cform import layout

from pmr2.app.interfaces import *
from pmr2.app.content import *

import form


class PMR2AddForm(form.AddForm):
    """\
    Repository root add form.
    """

    fields = z3c.form.field.Fields(IPMR2)
    clsobj = PMR2

    def add_data(self, ctxobj):
        ctxobj.title = self._data['title']
        # FIXME create root Hg dir if not exist?
        # - validation on path need to happen somewhere
        ctxobj.repo_root = self._data['repo_root']

    def post_add(self, ctxobj):
        """\
        Create the required container objects.

        It may be better to move this to profile if possible.
        """

        add_container(ctxobj, WorkspaceContainer)
        add_container(ctxobj, SandboxContainer)
        add_container(ctxobj, ExposureContainer)

PMR2AddFormView = layout.wrap_form(PMR2AddForm, label="Repository Add Form")


class PMR2EditForm(form.EditForm):
    """\
    Repository Edit Form.
    """

    fields = z3c.form.field.Fields(IPMR2)

# Plone Form wrapper for the EditForm
PMR2EditFormView = layout.wrap_form(PMR2EditForm, label="Repository Edit Form")

def add_container(context, clsobj):
    # helper method to construct the PMR2 internal containers
    obj = clsobj()
    context[obj.id] = obj
    # grab object from context
    obj = context[obj.id]
    obj.title = obj.id.title()
    obj.notifyWorkflowCreated()
    obj.reindexObject()
    return obj

