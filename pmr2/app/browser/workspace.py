import zope.app.pagetemplate.viewpagetemplatefile
import zope.component
import zope.publisher.browser

import z3c.form.interfaces
import z3c.form.field
import z3c.form.form
import z3c.form.value

from plone.app.z3cform import layout

from pmr2.app.interfaces import *
from pmr2.app.content import *

from widget import WorkspaceListingWidgetFactory
import form
import page
import table


# Workspace Container

class WorkspaceContainerAddForm(form.AddForm):
    """\
    Workspace container add form.
    """

    fields = z3c.form.field.Fields(IWorkspaceContainer).select(
        'title',
    )
    clsobj = WorkspaceContainer

    def add_data(self, ctxobj):
        ctxobj.title = self._data['title']

WorkspaceContainerAddFormView = layout.wrap_form(
    WorkspaceContainerAddForm, label="Workspace Container Add Form")


class WorkspaceContainerEditForm(form.EditForm):
    """\
    Workspace Container Edit form
    """

    fields = z3c.form.field.Fields(IWorkspaceContainer).select(
        'title',
    )

WorkspaceContainerEditFormView = layout.wrap_form(
    WorkspaceContainerEditForm, label="Workspace Container Management")


class WorkspaceContainerRepoListingForm(z3c.form.form.Form):
    """\
    Workspace Container Edit form
    """

    mode = z3c.form.interfaces.DISPLAY_MODE

    fields = z3c.form.field.Fields(IWorkspaceContainer).select(
        'get_repository_list',
    )
    fields['get_repository_list'].widgetFactory = WorkspaceListingWidgetFactory

WorkspaceContainerRepoListingFormView = layout.wrap_form(
    WorkspaceContainerRepoListingForm, label="Workspace Container Management")


# Workspace

class WorkspaceView(page.Simple):

    template = zope.app.pagetemplate.viewpagetemplatefile.ViewPageTemplateFile(
        'workspace.pt')


# XXX temporary.
WorkspaceFileView = WorkspaceView
WorkspaceRawfileView = WorkspaceView


class WorkspaceLogView(page.Simple):

    template = zope.app.pagetemplate.viewpagetemplatefile.ViewPageTemplateFile(
        'workspace_log.pt')

    def content(self):
        logs = self.context.get_log()
        t = table.ChangelogTable(logs, self.request)
        t.update()
        return t.render()


class WorkspaceAddForm(form.AddForm):
    """\
    Workspace add form.
    """

    fields = z3c.form.field.Fields(IWorkspaceAdd)
    clsobj = Workspace

    def add_data(self, ctxobj):
        ctxobj.title = self._data['title']
        ctxobj.description = self._data['description']

WorkspaceAddFormView = layout.wrap_form(
    WorkspaceAddForm, label="Workspace Creation Form")


class WorkspaceEditForm(form.EditForm):
    """\
    Workspace edit form.
    """

    fields = z3c.form.field.Fields(IWorkspace)

WorkspaceEditFormView = layout.wrap_form(
    WorkspaceEditForm, label="Workspace Edit Form")
