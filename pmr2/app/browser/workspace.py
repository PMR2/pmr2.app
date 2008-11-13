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


class WorkspaceContainerRepoListing(page.SimplePage):

    def content(self):

        # XXX these messages should be stored in/gathered from the
        # exception class/instance.
        # XXX could use an error template to wrap these error messages.
        try:
            repolist = self.context.get_repository_list()
        except RepoPathUndefinedError:
            return u'<div class="error">Repository Path is undefined.</div>'
        except WorkspaceDirNotExistsError:
            return u'<div class="error">Workspace path is missing. ' \
                    'Please notify administrator.</div>'

        t = table.WorkspaceStatusTable(repolist, self.request)
        t.update()
        return t.render()

WorkspaceContainerRepoListingView = layout.wrap_form(
    WorkspaceContainerRepoListing, label="Raw Workspace Listing")


# Workspace

class WorkspacePage(page.SimplePage):

    template = zope.app.pagetemplate.viewpagetemplatefile.ViewPageTemplateFile(
        'workspace.pt')

WorkspacePageView = layout.wrap_form(WorkspacePage)


# XXX temporary.
WorkspaceFileView = WorkspacePageView
WorkspaceRawfileView = WorkspacePageView


class WorkspaceLog(page.SimplePage):

    def content(self):
        logs = self.context.get_log()
        t = table.ChangelogTable(logs, self.request)
        t.update()
        return t.render()

WorkspaceLogView = layout.wrap_form(WorkspaceLog, label='Changelog Entries')


class WorkspaceShortlog(page.SimplePage):

    def content(self):
        logs = self.context.get_log(shortlog=True, datefmt='rfc3339date')
        t = table.ChangelogTable(logs, self.request)
        t.update()
        return t.render()

WorkspaceShortlogView = layout.wrap_form(WorkspaceShortlog, label='Shortlog')


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
