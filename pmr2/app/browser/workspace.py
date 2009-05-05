import warnings
import mimetypes

import zope.interface
import zope.component
import zope.event
import zope.lifecycleevent
import zope.app.pagetemplate.viewpagetemplatefile
import zope.publisher.browser
from zope.publisher.interfaces import NotFound

import z3c.form.interfaces
import z3c.form.field
import z3c.form.form
import z3c.form.value

from plone.z3cform import layout
from Products.CMFCore.utils import getToolByName

import pmr2.mercurial.exceptions
import pmr2.mercurial.utils
from pmr2.mercurial import Storage

from pmr2.app.interfaces import *
from pmr2.app.content import *
from pmr2.app.util import set_xmlbase, fix_pcenv_externalurl, obfuscate

import interfaces

import widget
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
        # need styling the first, current and last class of renderBatch
        return '\n'.join([t.render(), t.renderBatch()])

WorkspaceContainerRepoListingView = layout.wrap_form(
    WorkspaceContainerRepoListing, label="Raw Workspace Listing")


# Workspace

class WorkspacePage(page.SimplePage):
    """\
    The main page view.
    """
    # XXX the implementation works, but is probably not best practice
    # way to implement views based on other classes.

    template = zope.app.pagetemplate.viewpagetemplatefile.ViewPageTemplateFile(
        'workspace.pt')

    @property
    def owner(self):
        if not hasattr(self, '_owner'):
            owner = self.context.getOwner()
            result = '%s <%s>' % (
                owner.getProperty('fullname', owner.getId()),
                owner.getProperty('email', ''),
            )
            self._owner = obfuscate(result)

        return self._owner

    def shortlog(self):
        if not hasattr(self, '_log'):
            self._log = WorkspaceShortlog(self.context, self.request)
            # set our requirements.
            self._log.maxchanges = 10  # XXX magic number
            self._log.navlist = None
        return self._log()

    def exposure_list(self):
        pt = getToolByName(self.context, 'portal_catalog')
        d = {}
        d['pmr2_exposure_workspace'] = self.context.id
        return pt(**d)


WorkspacePageView = layout.wrap_form(
    WorkspacePage,
    __wrapper_class=page.BorderedStorageFormWrapper,
)


class WorkspaceLog(page.NavPage, z3c.table.value.ValuesForContainer):

    # XXX no this does not work
    # XXX need to hack context_fti or DynamicViewTypeInformation somehow
    # to make it do what needs to be done.
    # This value could be captured using DynamicViewTypeInformation
    # XXX this needs to be fixed to take advantage of shared adapted result.
    shortlog = False
    url_expr = '@@log'
    tbl = table.ChangelogTable
    maxchanges = None  # default value.
    datefmt = None # default value.

    @property
    def log(self):
        if not hasattr(self, '_log'):
            try:
                storage = zope.component.queryMultiAdapter(
                    (self.context, self.request, self), 
                    name="PMR2StorageRequestView",
                )
                self._log = storage.get_log(shortlog=self.shortlog,
                                            datefmt=self.datefmt,
                                            maxchanges=self.maxchanges)
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
        """\
        Although this is a property, it will return a method that 
        returns a generator.
        """

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


class WorkspaceLogRss(page.RssPage, WorkspaceLog):

    datefmt = 'rfc822date'

    def items(self):
        for i in self.values():
            yield {
                'title': i['desc'].splitlines()[0],
                # XXX magic manifest link
                'link': '%s/@@file/%s' % (
                    self.context.context.absolute_url(),
                    i['node'],
                ),
                'description': i['desc'],
                'author': obfuscate(i['author']),
                'pubDate': i['date'],
            }


class WorkspaceAddForm(form.AddForm):
    """\
    Workspace add form.
    """

    fields = z3c.form.field.Fields(IWorkspaceAdd)
    clsobj = Workspace

    def add_data(self, ctxobj):
        ctxobj.title = self._data['title']
        ctxobj.description = self._data['description']

        # XXX creating mercurial repository here.
        rp = ctxobj.get_path()
        Storage.create(rp, ffa=True)

WorkspaceAddFormView = layout.wrap_form(
    WorkspaceAddForm, label="Workspace Creation Form")


class WorkspaceBulkAddForm(z3c.form.form.AddForm):
    """\
    Workspace Bulk Add Form
    """

    @property
    def fields(self):
        fields = z3c.form.field.Fields(IWorkspaceBulkAdd)
        fields['workspace_list'].widgetFactory[
            z3c.form.interfaces.INPUT_MODE] = widget.TextAreaWidgetFactory
        return fields

    result_base = """\
      <dt>%s</dt>
      <dd>%d</dd>
    """

    failure_base = """
      <dt>%s</dt>
      <dd>
      <ul>
      %s
      </ul>
      </dd>
    """

    def completed(self):
        result = ['<p>The results of the bulk import:</p>', '<dl>']
        if self.created:
            result.append(self.result_base % ('Success', self.created))
        if self.existed:
            result.append(self.result_base % ('Existed', self.existed))
        if self.norepo:
            result.append(self.failure_base % ('Mercurial Repo Not Found',
            '\n'.join(['<li>%s</li>' % i for i in self.norepo]))
        )
        if self.failed:
            result.append(self.failure_base % ('Other Failure',
            '\n'.join(['<li>%s</li>' % i for i in self.failed]))
        )
        result.append('</dl>')
        return '\n'.join(result)

    def createAndAdd(self, data):
        self.created = self.existed = 0
        self.failed = []
        self.norepo = []

        workspaces = data['workspace_list'].splitlines()
        valid_hg = [i[0] for i in self.context.get_repository_list()]
        for id_ in workspaces:
            # unicode encoding needed here?
            id_ = str(id_)  # id_.encode('utf8')
            if not id_:
                continue
            if id_ not in valid_hg:
                # Only repo not found are reported as failures.
                self.norepo.append(id_)
                continue
            if id_ in self.context:
                self.existed += 1
                continue

            try:
                obj = Workspace(id_, **data)
                zope.event.notify(zope.lifecycleevent.ObjectCreatedEvent(obj))
                self.context[id_] = obj
                obj = self.context[id_]
                obj.title = id_.replace('_', ', ').title()
                obj.notifyWorkflowCreated()
                obj.reindexObject()
                self.created += 1
            except:
                # log stacktrace?
                self.failed.append(id_)

        # marking this as done.
        self._finishedAdd = True

    def nextURL(self):
        """\
        Go back to the Workspace Container
        """

        return self.context.absolute_url()

    def render(self):
        if self._finishedAdd:
            return self.completed()
        return super(WorkspaceBulkAddForm, self).render()

WorkspaceBulkAddFormView = layout.wrap_form(
    WorkspaceBulkAddForm, label="Workspace Bulk Creation Form")


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
    
    zope.interface.implements(interfaces.IWorkspaceFilePageView)

    url_expr = '@@file'
    filetemplate = \
        zope.app.pagetemplate.viewpagetemplatefile.ViewPageTemplateFile(
        'file.pt')

    @property
    def storage(self):
        if not hasattr(self, '_storage'):
            self._storage = zope.component.queryMultiAdapter(
                (self.context, self.request, self),
                name="PMR2StorageRequestView"
            )
        return self._storage

    # XXX rewrite this class to use adapters for specific views for 
    # these distinct types of values
    @property
    def values(self):
        """
        provides values for the table.
        """
        if self.storage.manifest:
            return self.storage.manifest['aentries']
        elif self.storage.fileinfo:
            return self.storage.fileinfo['text']
        return []

    def content(self):
        if self.storage.manifest is None and self.storage.fileinfo is None:
            raise NotFound(self.context, self.context.title_or_id(), 
                           self.request)

        if self.storage.manifest:
            t = table.FileManifestTable(self, self.request)
            t.update()
            return t.render()
        else:
            return self.filetemplate()

    @property
    def label(self):
        """
        provides values for the form.
        """
        if self.storage.manifest:
            label = 'Manifest'
        elif self.storage.fileinfo:
            label = 'Fileinfo'
        else:
            return u'No Information Available'
        return u'%s: %s @ %s / %s' % (
            label, self.context.title_or_id(), self.storage.rev[:10], 
            self.storage.path.replace('/', ' / '),
        )

    @property
    def rooturi(self):
        """the root uri."""
        return '/'.join([
            self.context.absolute_url(),
            '@@rawfile',
            self.storage.rev,
        ])

    @property
    def fullpath(self):
        """permanent uri."""
        return '/'.join([
            self.context.absolute_url(),
            '@@rawfile',
            self.storage.rev,
            self.storage.path,
        ])

WorkspaceFilePageView = layout.wrap_form(
    WorkspaceFilePage,
    __wrapper_class=page.BorderedTraverseFormWrapper,
)
# XXX WorkspaceFilePageView needs to implement
#zope.interface.implements(interfaces.IWorkspaceFilePageView)


class WorkspaceRawfileView(WorkspaceFilePage):

    def __call__(self):
        if self.storage.fileinfo is None:
            raise NotFound(self.context, self.context.title_or_id(), 
                           self.request)
        else:
            # not supporting resuming download
            # XXX large files will eat RAM
            data = self.storage.file
            mt = mimetypes.guess_type(self.storage.path)[0]
            if mt is None or (data and '\0' in data[:4096]):
                mt = mt or 'application/octet-stream'
            self.request.response.setHeader('Content-Type', mt)
            self.request.response.setHeader('Content-Length', len(data))
            return data


class WorkspaceRawfileXmlBaseView(WorkspaceRawfileView):

    def find_type(self):
        if self.storage.path.endswith('session.xml'):
            return 'application/x-pcenv-cellml+xml'

    def __call__(self):
        data = WorkspaceRawfileView.__call__(self)

        # add the xml:base, and append '/' to complete path
        data = set_xmlbase(data, self.rooturi + '/')

        if self.storage.path.endswith('session.xml'):
            # See pmr2.app.util.fix_pcenv_externalurl and
            # https://tracker.physiomeproject.org/show_bug.cgi?id=1079
            data = fix_pcenv_externalurl(data, self.rooturi)

        # all done, now set headers.
        contentType = self.find_type()
        filename = self.storage.path.split('/').pop()
        if contentType:
            self.request.response.setHeader('Content-Type', contentType)
        self.request.response.setHeader('Content-Disposition',
            'attachment; filename="%s"' % filename,
        )
        self.request.response.setHeader('Content-Length', len(data))

        return data


class WorkspaceRawfileXmlBasePCEnvView(WorkspaceRawfileXmlBaseView):

    def find_type(self):
        # XXX we are not doing this for every single type, alternate
        # solution will be done.
        return 'application/x-pcenv-cellml+xml'


class CreateForm(z3c.form.form.Form):

    # XXX implement the interface that will show the types that users
    # can create from a workspace.

    def __call__(self):
        type = self.request.form.get('type', None)
        rev = self.request.form.get('rev', None)
        workspace = self.request.form.get('workspace', None)
        if type == 'exposure':
            # XXX magic creation view
            subfrag = ('exposure', '@@exposure_add_form',)
            url = '/'.join(self.context.getPhysicalPath()[0:-2] + subfrag)
            url += '?form.widgets.workspace=%s&form.widgets.commit_id=%s' % (
                workspace,
                rev,
            )
            return self.request.response.redirect(url)

        # XXX call parent's __call__ to render the form
        return u''

CreateFormView = layout.wrap_form(
    CreateForm, label="Object Creation Form")
