import zope.app.pagetemplate.viewpagetemplatefile
import zope.component
import zope.publisher.browser
from zope.publisher.interfaces import NotFound

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


class WorkspaceLog(page.NavPage):

    # XXX no this does not work
    # XXX need to hack context_fti or DynamicViewTypeInformation somehow
    # to make it do what needs to be done.
    # This value could be captured using DynamicViewTypeInformation
    shortlog = False
    url_expr = '@@log'
    tbl = table.ChangelogTable

    @property
    def rev(self):
        # getting revision here as the reassignment of traverse_subpath
        # happens after the object is initiated by the wrapper.
        if self.traverse_subpath:
            return '/'.join(self.traverse_subpath)

    @property
    def log(self):
        if not hasattr(self, '_log'):
            try:
                self._log = self.context.get_log(rev=self.rev,
                                                 shortlog=self.shortlog)
            except:  # XXX assume RevisioNotFound
                raise NotFound(self.context, self.rev, self.request)
        return self._log

    def navlist(self):
        nav = self.log['changenav']
        for i in nav():
            yield {
                'href': i['node'],
                'label': i['label'],
            }

    def content(self):
        entries = self.log['entries']()
        t = self.tbl(entries, self.request, self.context.absolute_url())
        t.update()
        return t.render()

WorkspaceLogView = layout.wrap_form(
    WorkspaceLog, 
    __wrapper_class=page.TraverseFormWrapper,
    label='Changelog Entries'
)

class WorkspaceShortlog(WorkspaceLog):

    shortlog = True
    url_expr = '@@shortlog'
    tbl = table.ShortlogTable

WorkspaceShortlogView = layout.wrap_form(
    WorkspaceShortlog,
    __wrapper_class=page.TraverseFormWrapper,
    label='Shortlog'
)


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
