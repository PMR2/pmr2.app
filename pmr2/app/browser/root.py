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
        """

        # XXX somehow make this part of the profile like new plone site
        # will create the default contents?
        # FIXME - less magic string
        ws_c = WorkspaceContainer('workspace')
        sb_c = SandboxContainer('sandbox')
        ex_c = ExposureContainer('exposure')
        ws_c.title = 'Workspace'
        sb_c.title = 'Sandbox'
        ex_c.title = 'Exposure'
        ctxobj['workspace'] = ws_c
        ctxobj['sandbox'] = sb_c
        ctxobj['exposure'] = ex_c
        ws_c.notifyWorkflowCreated()
        sb_c.notifyWorkflowCreated()
        ex_c.notifyWorkflowCreated()
        ws_c.reindexObject()
        sb_c.reindexObject()
        ex_c.reindexObject()

    def nextURL(self):
        return "%s/%s" % (self.context.absolute_url(), self._name)

PMR2AddFormView = layout.wrap_form(PMR2AddForm, label="Repository Add Form")


class PMR2EditForm(form.EditForm):
    """\
    Repository Edit Form.
    """

    fields = z3c.form.field.Fields(IPMR2)

# Plone Form wrapper for the EditForm
PMR2EditFormView = layout.wrap_form(PMR2EditForm, label="Repository Edit Form")
