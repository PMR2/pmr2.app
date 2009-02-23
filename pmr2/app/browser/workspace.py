import mimetypes

import zope.interface
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
import pmr2.mercurial.utils

from pmr2.app.interfaces import *
from pmr2.app.content import *
from pmr2.app.util import set_xmlbase, fix_pcenv_externalurl

import interfaces

from widget import WorkspaceListingWidgetFactory
import form
import page
import mixin
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

WorkspacePageView = layout.wrap_form(
    WorkspacePage,
    __wrapper_class=page.BorderedFormWrapper,
)

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
        if not self.traverse_subpath:
            return None
        return self.traverse_subpath[0]

    @property
    def log(self):
        if not hasattr(self, '_log'):
            try:
                self._log = self.context.get_log(rev=self.rev,
                                                 shortlog=self.shortlog)
            except pmr2.mercurial.exceptions.RevisionNotFound:
                raise NotFound(self.context, self.context.title_or_id(), 
                               self.request)
        return self._log

    def navlist(self):
        nav = self.log['changenav']
        for i in nav():
            yield {
                'href': i['node'],
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
    __wrapper_class=page.BorderedTraverseFormWrapper,
    label='Changelog Entries'
)


class WorkspaceShortlog(WorkspaceLog):

    shortlog = True
    url_expr = '@@shortlog'
    tbl = table.ShortlogTable

WorkspaceShortlogView = layout.wrap_form(
    WorkspaceShortlog,
    __wrapper_class=page.BorderedTraverseFormWrapper,
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


class WorkspaceFilePage(page.TraversePage, z3c.table.value.ValuesForContainer,
        mixin.PMR2MercurialPropertyMixin):
    """\
    Manifest listing page.
    """
    
    zope.interface.implements(interfaces.IWorkspaceFilePageView)

    url_expr = '@@file'
    filetemplate = \
        zope.app.pagetemplate.viewpagetemplatefile.ViewPageTemplateFile(
        'file.pt')

    @property
    def rev(self):
        if hasattr(self, '_rev'):
            return self._rev
        # bootstrapping _rev for manifest or fileinfo, as it depends on this
        self._rev = None
        if self.traverse_subpath:
            self._rev = self.traverse_subpath[0]
        try:
            if self.manifest:
                self._rev = self.manifest['node']
            elif self.fileinfo:
                self._rev = self.fileinfo['node']
        except pmr2.mercurial.exceptions.RevisionNotFound:
            # cannot resolve to valid revision
            raise NotFound(self.context, self.context.title_or_id(), 
                           self.request)
        return self._rev

    @property
    def path(self):
        if hasattr(self, '_path'):
            return self._path
        self._path = ''
        if self.traverse_subpath:
            self._path = '/'.join(self.traverse_subpath[1:])
        return self._path

    # XXX rewrite this class to use adapters for specific views for 
    # these distinct types of values
    @property
    def values(self):
        if self.manifest:
            return self.manifest['aentries']
        elif self.fileinfo:
            return self.fileinfo['text']
        return []

    def content(self):
        if self.manifest is None and self.fileinfo is None:
            raise NotFound(self.context, self.context.title_or_id(), 
                           self.request)

        if self.manifest:
            t = table.FileManifestTable(self, self.request)
            t.update()
            return t.render()
        else:
            return self.filetemplate()

    @property
    def label(self):
        if self.manifest:
            label = 'Manifest'
        elif self.fileinfo:
            label = 'Fileinfo'
        else:
            return u'No Information Available'
        return u'%s: %s @ %s / %s' % (
            label, self.context.title_or_id(), self.rev[:10], 
            self.path.replace('/', ' / '),
        )

    @property
    def rooturi(self):
        """the root uri."""
        return '/'.join([
            self.context.absolute_url(),
            '@@rawfile',
            self.rev,
        ])

    @property
    def fullpath(self):
        """permanent uri."""
        return '/'.join([
            self.context.absolute_url(),
            '@@rawfile',
            self.rev,
            self.path,
        ])

WorkspaceFilePageView = layout.wrap_form(
    WorkspaceFilePage,
    __wrapper_class=page.BorderedTraverseFormWrapper,
)
# XXX WorkspaceFilePageView needs to implement
#zope.interface.implements(interfaces.IWorkspaceFilePageView)


class WorkspaceRawfileView(WorkspaceFilePage):

    def __call__(self):
        if self.fileinfo is None:
            raise NotFound(self.context, self.context.title_or_id(), 
                           self.request)
        else:
            # not supporting resuming download
            # XXX large files will eat RAM
            data = self.storage.file(self.rev, self.path)
            mt = mimetypes.guess_type(self.path)[0]
            if mt is None or (data and '\0' in data[:4096]):
                mt = mt or 'application/octet-stream'
            self.request.response.setHeader('Content-Type', mt)
            self.request.response.setHeader('Content-Length', len(data))
            return data


class WorkspaceRawfileXmlBaseView(WorkspaceRawfileView):

    def find_type(self):
        if self.path.endswith('session.xml'):
            return 'application/x-pcenv-cellml+xml'

    def __call__(self):
        data = WorkspaceRawfileView.__call__(self)

        # add the xml:base, and append '/' to complete path
        data = set_xmlbase(data, self.rooturi + '/')

        if self.path.endswith('session.xml'):
            # See pmr2.app.util.fix_pcenv_externalurl and
            # https://tracker.physiomeproject.org/show_bug.cgi?id=1079
            data = fix_pcenv_externalurl(data, self.rooturi)

        # all done, now set headers.
        contentType = self.find_type()
        filename = self.path.split('/').pop()
        if contentType:
            self.request.response.setHeader('Content-Type', contentType)
        self.request.response.setHeader('Content-Disposition',
            'attachment; filename="%s"' % filename,
        )
        self.request.response.setHeader('Content-Length', len(data))

        return data
                

class CreateForm(z3c.form.form.Form):

    # XXX implement the interface that will show the types that users
    # can create from a workspace.

    def __call__(self):
        type = self.request.form.get('type', None)
        rev = self.request.form.get('rev', None)
        workspace = self.request.form.get('workspace', None)
        if type == 'exposure':
            # XXX magic creation view
            url = '/'.join([
                self.context.get_pmr2_container().absolute_url(),
                'exposure',
                '@@exposure_add_form',
            ]) 
            url += '?form.widgets.workspace=%s&form.widgets.commit_id=%s' % (
                workspace,
                rev,
            )
            return self.request.response.redirect(url)

        # XXX call parent's __call__ to render the form
        return u''

CreateFormView = layout.wrap_form(
    CreateForm, label="Object Creation Form")
