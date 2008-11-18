import zope.app.pagetemplate.viewpagetemplatefile
import zope.component
import zope.publisher.browser
from zope.publisher.interfaces import NotFound

import z3c.form.interfaces
import z3c.form.field
import z3c.form.form
import z3c.form.value

from plone.app.z3cform import layout

import pmr2.mercurial.exceptions

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
WorkspaceRawfileView = WorkspacePageView


class WorkspaceLog(page.NavPage, z3c.table.value.ValuesForContainer):

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
            rev = self.traverse_subpath[0]
            if rev[0] != '@':
                raise NotFound(self.context, self.context.title_or_id(), 
                               self.request)
            return rev[1:]

    @property
    def log(self):
        if not hasattr(self, '_log'):
            try:
                self._log = self.context.get_log(rev=self.rev,
                                                 shortlog=self.shortlog)
            except:  # XXX assume RevisionNotFound
                raise NotFound(self.context, self.context.title_or_id(), 
                               self.request)
        return self._log

    def navlist(self):
        nav = self.log['changenav']
        for i in nav():
            yield {
                'href': '@' + i['node'],
                'label': i['label'],
            }

    @property
    def values(self):
        return self.log['entries']

    def content(self):
        t = self.tbl(self, self.request)
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


class WorkspaceFilePage(page.TraversePage, z3c.table.value.ValuesForContainer):
    """\
    Manifest listing page.
    """

    url_expr = '@@file'

    @property
    def rev(self):
        # getting revision here as the reassignment of traverse_subpath
        # happens after the object is initiated by the wrapper.
        if self.traverse_subpath:
            rev = self.traverse_subpath[0]
            if rev[0] != '@':
                # redirect to latest rev
                raise NotFound(self.context, self.context.title_or_id(), 
                               self.request)
            return rev[1:]

    @property
    def path(self):
        path = ''
        if self.traverse_subpath:
            path = '/'.join(self.traverse_subpath[1:])
            return path
        # redirect

    @property
    def manifest(self):
        rev = self.rev
        path = self.path
        if not rev:
            # redirect
            pass
            #raise NotFound(self.context, self.context.title_or_id(), 
            #               self.request)
        if not hasattr(self, '_manifest'):
            try:
                self._storage = self.context.get_storage()
                self._manifest = self._storage.manifest(rev, path).next()
            except pmr2.mercurial.exceptions.PathNotFound:
                self._manifest = None
        return self._manifest

    @property
    def file(self):
        return None

    @property
    def values(self):
        return self.manifest['aentries']

    def content(self):
        if self.manifest is None and self.file is None:
            raise NotFound(self.context, self.context.title_or_id(), 
                           self.request)

        if self.manifest:
            t = table.FileManifestTable(self, self.request)
            t.update()
            return t.render()

        else:
            # XXX File rendering.
            return u''

WorkspaceFilePageView = layout.wrap_form(
    WorkspaceFilePage,
    __wrapper_class=page.TraverseFormWrapper,
    label='Manifest'
)
