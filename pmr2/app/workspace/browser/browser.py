from os.path import join
import warnings
import mimetypes
import urllib

import zope.interface
import zope.component
import zope.event
import zope.lifecycleevent
import zope.publisher.browser
from zope.i18nmessageid import MessageFactory
_ = MessageFactory("pmr2")

from zope.app.pagetemplate.viewpagetemplatefile \
    import ViewPageTemplateFile as VPTF
ViewPageTemplateFile = lambda p: VPTF(join('templates', p))

from paste.httpexceptions import HTTPNotFound, HTTPFound

import z3c.form.interfaces
import z3c.form.field
import z3c.form.form
import z3c.form.value
import z3c.form.button

from plone.z3cform import layout
from Products.CMFCore.utils import getToolByName
from Acquisition import aq_parent, aq_inner

from pmr2.app.workspace.interfaces import *
from pmr2.app.workspace.content import *
from pmr2.app.util import set_xmlbase, obfuscate, isodate

from pmr2.app.browser import interfaces
from pmr2.app.browser import form
from pmr2.app.browser import page

from pmr2.app.browser.layout import BorderedTraverseFormWrapper
from pmr2.app.browser.layout import TraverseFormWrapper

from pmr2.app.workspace import table
from pmr2.app.workspace.exceptions import *
from pmr2.app.workspace.interfaces import *
from pmr2.app.workspace.browser.interfaces import *
from pmr2.app.workspace.browser.layout import BorderedStorageFormWrapper


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
        t = table.WorkspaceStatusTable(self.context, self.request)
        # XXX no idea why this isn't done automatically
        t.__name__ = self.__name__
        try:
            t.update()
            # need styling the first, current and last class of renderBatch
            return '\n'.join([t.render(), t.renderBatch()])
        except PathLookupError:
            return u'<div class="error">Repository Path lookup failed.</div>'
        except RepoPathUndefinedError:
            # this may be made obsolete by the previous error.
            return u'<div class="error">Repository Path is undefined.</div>'
        except WorkspaceDirNotExistsError:
            return u'<div class="error">Workspace path is missing. ' \
                    'Please notify administrator.</div>'


WorkspaceContainerRepoListingView = layout.wrap_form(
    WorkspaceContainerRepoListing, label="Raw Workspace Listing")


# Workspace


class WorkspaceTraversePage(page.TraversePage):
    """\
    Parses traversal path in a way specific to Workspace paths.
    """

    def publishTraverse(self, request, name):
        # customize traverse subpath here as we can set the request
        # variables directly
        self.traverse_subpath.append(name)
        if self.request.get('rev', None) is None:
            self.request['rev'] = name
            self.request['request_subpath'] = []
        else:
            self.request['request_subpath'].append(name)
        return self


class WorkspaceProtocol(zope.publisher.browser.BrowserPage):
    """\
    Browser page to provide raw access to the protocol of this given
    workspace.
    """

    # XXX this class is currently unused until the permissions can be
    # totally handled "correctly".

    def __call__(self, *a, **kw):
        storage = zope.component.getAdapter(self.context, IStorage)

        try:
            # Process the request.
            return storage.process_request(self.request)
        except UnsupportedCommandError:
            # Can't do this command, redirect back to root object.
            raise HTTPFound(self.context.absolute_url())


class WorkspaceArchive(WorkspaceTraversePage):
    """\
    Browser page that archives a hg repo.
    """

    def __call__(self, *a, **kw):
        try:
            storage = zope.component.getAdapter(self.context, IStorage)
        except ValueError:
            # as this is a deep linked page, if whatever was broken 
            # further up there wouldn't have been links down to this
            # point here.
            raise HTTPNotFound(self.context.title_or_id())

        # ignoring subrepo functionality for now.
        # subrepo = self.request.form.get('subrepo', False)

        try:
            storage.checkout(self.request.get('rev', None))
        except RevisionNotFoundError:
            raise HTTPNotFound(self.context.title_or_id())

        request_subpath = self.request.get('request_subpath', [])
        if not request_subpath:
            # no archive type
            raise HTTPNotFound(self.context.title_or_id())
        type_ = request_subpath[0]

        # this is going to hurt so bad if this was a huge archive...
        archivestr = storage.archive(type_)

        info = storage.archiveInfo(type_)
        headers = [
            ('Content-Type', info['mimetype']),
            ('Content-Length', len(archivestr)),
            ('Content-Disposition', 'attachment; filename=%s%s' % (
                self.context.id, info['ext'])),
        ]

        for header in headers:
            self.request.response.setHeader(*header)

        return archivestr


class WorkspacePage(page.SimplePage):
    """\
    The main workspace page.
    """

    template = ViewPageTemplateFile('workspace.pt')

    @property
    def owner(self):
        if not hasattr(self, '_owner'):
            # method getOwner is from AccessControl.Owned.Owned
            owner = self.context.getOwner()
            result = '%s <%s>' % (
                owner.getProperty('fullname', owner.getId()),
                owner.getProperty('email', ''),
            )
            self._owner = obfuscate(result)

        return self._owner

    def shortlog(self):
        if not hasattr(self, '_log'):
            # XXX aq_inner(self.context) not needed?
            self._log = WorkspaceShortlog(self.context, self.request)
            # set our requirements.
            self._log.maxchanges = 10  # XXX magic number
            self._log.navlist = None
        return self._log()


WorkspacePageView = layout.wrap_form(
    WorkspacePage,
    __wrapper_class=BorderedStorageFormWrapper,
)


class WorkspaceLog(WorkspaceTraversePage):

    zope.interface.implements(IWorkspaceLogProvider)

    # Ideally, we acquire the table needed dynamically, based on the
    # requested URI.
    shortlog = False
    tbl = table.ChangelogTable
    maxchanges = 50  # default value.
    datefmt = None # default value.

    def content(self):
        # putting datefmt into request as the value provider for the
        # table currently uses it to determine output format...
        self.request['datefmt'] = self.datefmt
        self.request['maxchanges'] = self.maxchanges

        t = self.tbl(self.context, self.request)
        # the parent of the table is this form.
        t.__parent__ = self
        t.update()
        return t.render()

WorkspaceLogView = layout.wrap_form(
    WorkspaceLog, 
    __wrapper_class=BorderedTraverseFormWrapper,
    label='Changelog Entries'
)


class WorkspaceShortlog(WorkspaceLog):

    shortlog = True
    tbl = table.ShortlogTable

WorkspaceShortlogView = layout.wrap_form(
    WorkspaceShortlog,
    __wrapper_class=BorderedTraverseFormWrapper,
    label='Shortlog'
)


#class WorkspacePageShortlog(WorkspaceShortlog):
#    # for workspace main listing.
#
#    tbl = table.WorkspacePageShortlogTable
#

class WorkspaceLogRss(page.RssPage):

    shortlog = False
    maxchanges = 50  # default value.

    def items(self):
        storage = zope.component.queryAdapter(self.context, IStorage)
        storage.datefmt = 'rfc2822'
        entries = storage.log(storage.rev, self.maxchanges)
        for i in entries:
            yield {
                'title': i['desc'].splitlines()[0],
                # XXX magic manifest link
                'link': '%s/@@file/%s' % (
                    self.context.absolute_url(),
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

    fields = z3c.form.field.Fields(interfaces.IObjectIdMixin) + \
             z3c.form.field.Fields(IWorkspace)
    clsobj = Workspace

    def add_data(self, ctxobj):
        ctxobj.title = self._data['title']
        ctxobj.description = self._data['description']
        ctxobj.storage = self._data['storage']

WorkspaceAddFormView = layout.wrap_form(
    WorkspaceAddForm, label="Workspace Object Creation Form")


class WorkspaceStorageCreateForm(WorkspaceAddForm):
    """\
    Workspace add form.  This also creates the storage object.
    """

    # IWorkspaceStorageCreate has a validator attached to its id 
    # attribute to verify that the workspace id has not been taken yet.
    fields = z3c.form.field.Fields(IWorkspaceStorageCreate) + \
             z3c.form.field.Fields(IWorkspace)

    def add_data(self, ctxobj):
        WorkspaceAddForm.add_data(self, ctxobj)
        storage = zope.component.getUtility(
            IStorageUtility, name=ctxobj.storage)
        storage.create(ctxobj)

WorkspaceStorageCreateFormView = layout.wrap_form(
    WorkspaceStorageCreateForm, label="Create a New Workspace")


class WorkspaceBulkAddForm(z3c.form.form.AddForm):
    """\
    Workspace Bulk Add Form

    XXX - this function is NOT maintained.
    """

    fields = z3c.form.field.Fields(IWorkspaceBulkAdd)

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
            result.append(self.failure_base % ('Repo Not Found',
            '\n'.join(['<li>%s</li>' % i for i in self.norepo]))
        )
        if self.failed:
            result.append(self.failure_base % ('Other Failure',
            '\n'.join(['<li>%s</li>' % i for i in self.failed]))
        )
        result.append('</dl>')
        return '\n'.join(result)

    def createAndAdd(self, data):
        # XXX this method does not assign workspace storage backend.
        self.created = self.existed = 0
        self.failed = []
        self.norepo = []

        workspaces = data['workspace_list'].splitlines()
        listing = zope.component.getAdapter(self.context, IWorkspaceListing)
        valid_hg = [i[0] for i in listing()]
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

    fields = z3c.form.field.Fields(IWorkspace).omit('storage')

WorkspaceEditFormView = layout.wrap_form(
    WorkspaceEditForm, label="Workspace Edit Form")


class FileInfoPage(WorkspaceTraversePage):
    """\
    A Traversal Page that extracts and process the info when updated.
    Provides some properties that is available once that is done.
    """

    template = ViewPageTemplateFile('workspace_file_page.pt')

    def absolute_url(self):
        return self.context.absolute_url()

    @property
    def rev(self):
        return self.request.get('rev', '')

    @property
    def shortrev(self):
        return self.request.get('shortrev', '')

    @property
    def data(self):
        return self.request.get('_data', {})

    def _getpath(self, view='rawfile', path=None):
        result = [
            self.context.absolute_url(),
            view,
            self.rev,
        ]
        if path:
            result.append(path)
        return result

    @property
    def rooturi(self):
        """the root uri."""
        return '/'.join(self._getpath())

    @property
    def fullpath(self):
        """permanent uri."""
        return '/'.join(self._getpath(path=self.data['file']))

    @property
    def viewpath(self):
        """view uri."""
        return '/'.join(self._getpath(view='file',
            path=self.data['file']))

    def update(self):
        """\
        Acquire content from request_subpath from storage
        """

        storage = zope.component.getAdapter(self.context, IStorage)
        try:
            storage.checkout(self.request.get('rev', None))
        except RevisionNotFoundError:
            raise HTTPNotFound(self.context.title_or_id())

        request_subpath = self.request.get('request_subpath', [])

        try:
            # to do a subrepo redirect, the implementation specific 
            # pathinfo method should raise a HTTPFound at this stage.
            data = storage.pathinfo('/'.join(request_subpath))
        except PathNotFoundError:
            raise HTTPNotFound(self.context.title_or_id())

        # update rev using the storage rev
        self.request['rev'] = storage.rev
        self.request['shortrev'] = storage.shortrev
        # this is for rendering
        self.request['filepath'] = request_subpath or ['']
        # data
        self.request['_data'] = data
        self.request['_storage'] = storage

FileInfoPageView = layout.wrap_form(
    FileInfoPage,
    __wrapper_class=BorderedTraverseFormWrapper,
)


class WorkspaceRawfileView(FileInfoPage):

    def __call__(self):
        self.update()
        data = self.request['_data']
        if data:
            # not supporting resuming download
            # XXX large files will eat RAM
            contents = data['contents']()

            if not isinstance(contents, basestring):
                # this is a rawfile view, this can be triggered by 
                # attempting to access a directory.  we redirect to the
                # standard file view.
                raise HTTPFound(self.viewpath)

            self.request.response.setHeader('Content-Type', data['mimetype']())
            self.request.response.setHeader('Content-Length', data['size'])
            return contents
        else:
            raise HTTPNotFound(self.context.title_or_id())


class WorkspaceRawfileXmlBaseView(WorkspaceRawfileView):

    @property
    def xmlrooturi(self):
        """the root uri."""
        return '/'.join(self._getpath(view='xmlbase'))

    def __call__(self):
        # XXX should really hook into a mimetype registry and not hard
        # coded in here.
        def custom_content_type(s):
            f_ext = (
                ('.session.xml', 'application/x-pcenv-cellml+xml'),
                ('.cellml', 'application/cellml+xml'),
            )
            for k, v in f_ext:
                if s.endswith(k):
                    self.request.response.setHeader('Content-Type', v)
                    return

        data = WorkspaceRawfileView.__call__(self)
        filepath = self.request['filepath']
        filename = filepath[-1]
        # have to acquire dirpath.
        request_subpath = self.request.get('request_subpath', [])
        dirpath = '/'.join(request_subpath[:-1] + [''])

        # add the xml:base, with empty end string for trailing /
        # since this is the xml base rewrite, we be consistent.
        xmlroot = '/'.join((self.xmlrooturi, dirpath,))
        data = set_xmlbase(data, xmlroot)

        # XXX this should not be here
        custom_content_type(filename)

        self.request.response.setHeader('Content-Disposition',
            'attachment; filename="%s"' % filename,
        )
        self.request.response.setHeader('Content-Length', len(data))

        return data
