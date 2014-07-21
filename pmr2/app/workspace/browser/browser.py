from os.path import join
import warnings
import mimetypes
import urllib

import zope.interface
import zope.component
import zope.event
import zope.lifecycleevent
import zope.publisher.browser

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile as VPTF
ViewPageTemplateFile = lambda p: VPTF(join('templates', p))

from zope.publisher.interfaces import NotFound, Redirect, BadRequest

import z3c.form.interfaces
import z3c.form.field
import z3c.form.form
import z3c.form.value
from z3c.form import button

from AccessControl import getSecurityManager
from AccessControl import Unauthorized
from Products.CMFCore.utils import getToolByName
from DateTime import DateTime
from Acquisition import aq_parent, aq_inner
from Products.statusmessages.interfaces import IStatusMessage

from pmr2.z3cform import form
from pmr2.z3cform import page

from pmr2.idgen.interfaces import IIdGenerator

from pmr2.app.settings.interfaces import IPMR2GlobalSettings

from pmr2.app.interfaces.exceptions import *

from pmr2.app.browser.interfaces import IObjectIdMixin
from pmr2.app.browser.page import NavPage, RssPage

from pmr2.app.workspace import table
from pmr2.app.workspace.exceptions import *
from pmr2.app.workspace.interfaces import *
from pmr2.app.workspace.content import *
from pmr2.app.workspace.i18n import MessageFactory as _
from pmr2.app.workspace.browser.util import *
from pmr2.app.workspace.browser.interfaces import *


# Workspace Container

class WorkspaceContainerAddForm(form.AddForm):
    """\
    Workspace container add form.
    """

    fields = z3c.form.field.Fields(IWorkspaceContainer).select(
        'title',
    )
    clsobj = WorkspaceContainer
    label = "Workspace Container Add Form"

    def add_data(self, ctxobj):
        ctxobj.title = self._data['title']


class WorkspaceContainerEditForm(form.EditForm):
    """\
    Workspace Container Edit form
    """

    fields = z3c.form.field.Fields(IWorkspaceContainer).select(
        'title',
    )

    label = "Workspace Container Management"


class WorkspaceContainerRepoListing(page.SimplePage):

    label = "Raw Workspace Listing"

    def template(self):
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

    protocol = None
    enabled = False

    def _queryPermission(self):
        # as I couldn't find the documentation on a utility that will
        # return the permission registered in the zcml, I copied this
        # from some other package because they do the same thing when
        # they need to figure out the permission of this class.
        permissions = getattr(self.__class__, '__ac_permissions__', [])
        for permission, methods in permissions:
            if methods[0] in ('', '__call__'):
                return permission

    def _checkPermission(self):
        # manual permission check.  This will need to be here until
        # we are provided a smarter way that will handle these things
        # based on protocols.
        permission = self._queryPermission()

        # this is the main security check, but it doesn't take into
        # account of roles...
        main = getSecurityManager().checkPermission(permission, self)

        # and so we need this hackish thing here if this is a post or
        # we already authenticated already
        if self.request.method in ['GET'] or main:
            return main

        # role checking...
        pm = getToolByName(self.context, 'portal_membership')
        user = pm.getAuthenticatedMember()
        if pm.isAnonymousUser():
            # don't want to deal with anonymous non GETs
            return False

        user_roles = user.getRolesInContext(self.context)
        # user either requires a role granted via @@sharing or has the
        # permission set manually under management.
        # FIXME remove Mercurial reference
        return u'WorkspacePusher' in user_roles or \
            user.has_permission('Mercurial Push', self.context)

        # I really wish this isn't such a horrible mess and without such
        # non-agnostic names.

    def update(self):
        if not self._checkPermission():
            raise Unauthorized()

        try:
            self.protocol = zope.component.getMultiAdapter(
                (self.context, self.request), IStorageProtocol)
        except UnknownStorageTypeError, e:
            status = IStatusMessage(self.request)
            status.addStatusMessage(
                u'The backend storage utility `%s` is missing. '
                 'Please contact site administrator.' % e[1])
            return

    def enabled(self):
        return self.protocol.enabled

    def render(self):
        # Warning: this method is used to manipulate data inside the
        # underlying storage backend.
        try:
            results = self.protocol()
        except UnsupportedCommandError:
            raise BadRequest('unsupported command')
        except ProtocolError:
            raise BadRequest('unsupported command')

        # We are successful, manually fire off an event until that
        # system is fully in place.
        if results.event == 'push':
            # XXX post push hooks?
            self.context.setModificationDate(DateTime())
            self.context.reindexObject()

        return results.result

    def __call__(self, *a, **kw):
        self.update()
        return self.render()


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
            raise NotFound(self.context, self.context.title_or_id())

        # ignoring subrepo functionality for now.
        # subrepo = self.request.form.get('subrepo', False)

        try:
            storage.checkout(self.request.get('rev', None))
        except RevisionNotFoundError:
            raise NotFound(self.context, self.context.title_or_id())

        request_subpath = self.request.get('request_subpath', [])
        if not request_subpath:
            # no archive type
            raise NotFound(self.context, self.context.title_or_id())
        type_ = request_subpath[0]

        try:
            try:
                info = storage.archiveInfo(type_)
                # this is going to hurt so bad if this was a huge archive...
                archivestr = storage.archive(type_)
                headers = [
                    ('Content-Type', info['mimetype']),
                    ('Content-Length', len(archivestr)),
                    ('Content-Disposition', 'attachment; filename="%s%s"' % (
                        self.context.id, info['ext'])),
                ]
            except ValueError:
                # get the utility
                au = zope.component.queryUtility(IStorageArchiver, type_)
                errormsg = None

                if au is None:
                    errormsg = (u'The archive format `%s` is unsupported' %
                        type_)

                if not au.enabledFor(storage):
                    errormsg = (u'The archive format `%s` is not supported '
                        'for this changeset' % type_)

                if errormsg:
                    status = IStatusMessage(self.request)
                    status.addStatusMessage(errormsg)
                    self.request.response.redirect(self.context.absolute_url())
                    return

                archivestr = au.archive(storage)

                headers = [
                    ('Content-Type', au.mimetype),
                    ('Content-Length', len(archivestr)),
                    ('Content-Disposition', 'attachment; filename="%s%s"' % (
                        self.context.id, au.suffix)),
                ]
        except StorageArchiveError as e:
            status = IStatusMessage(self.request)
            status.addStatusMessage(
                u'`%s` not accessible for archiving.' % str(e))
            self.request.response.redirect(self.context.absolute_url())

        for header in headers:
            self.request.response.setHeader(*header)

        return archivestr


class WorkspacePage(page.SimplePage):
    """\
    The main workspace page.
    """

    # XXX this need to implement an interface that allow omittance of
    # CMS chrome.

    zope.interface.implements(IWorkspacePage)

    # need interface for this page that handles storage protocol?
    template = ViewPageTemplateFile('workspace.pt')
    error_template = ViewPageTemplateFile('workspace_error.pt')
    protocolView = None
    shortlog_maxchange = 10

    def update(self):
        """\
        As the protocol level of the storage backend may do manipulation
        via GET or POST, we redirect the requests firstly to the defined
        form adapters appropriated for this task.
        """

        self.request['enable_border'] = True

        if self.request.method in ['POST']:
            view = zope.component.queryMultiAdapter(
                (self.context, self.request), name='protocol_write')
        else:
            view = zope.component.queryMultiAdapter(
                (self.context, self.request), name='protocol_read')

        # the view above should have safeguarded this...
        self.protocolView = view
        self.protocolView.update()

    @property
    def description(self):
        return self.context.description

    @property
    def owner(self):
        if not hasattr(self, '_owner'):
            # method getOwner is from AccessControl.Owned.Owned
            owner = self.context.getOwner()
            fullname = owner.getProperty('fullname', owner.getId())
            email = owner.getProperty('email', None)
            if email:
                result = '%s <%s>' % (fullname, email)
            else:
                result = fullname
            self._owner = obfuscate(result)

        return self._owner

    def shortlog(self):
        if not hasattr(self, '_log'):
            # XXX aq_inner(self.context) not needed?
            self._log = WorkspaceShortlog(self.context, self.request)
            # set our requirements.
            self._log.maxchanges = self.shortlog_maxchange
            self._log.navlist = None
        return self._log()

    def render(self):
        if self.protocolView.enabled():
            return self.protocolView.render()

        try:
            storage = zope.component.getAdapter(self.context, IStorage)
        except PathInvalidError:
            # well it appears there were problems getting the adapter,
            # so switch to error template.
            self.template = self.error_template
        return super(WorkspacePage, self).render()


class WorkspaceLog(WorkspaceTraversePage, NavPage):

    zope.interface.implements(IWorkspaceLogProvider)

    # Ideally, we acquire the table needed dynamically, based on the
    # requested URI.
    shortlog = False
    tbl = table.ChangelogTable
    maxchanges = 50  # default value.
    datefmt = None # default value.
    label = 'Changelog Entries'

    def update(self):
        self.request['enable_border'] = True

        self.request['shortlog'] = self.shortlog
        self.request['datefmt'] = self.datefmt
        self.request['maxchanges'] = self.maxchanges

        t = self.tbl(self.context, self.request)
        # the parent of the table is this form.
        t.__parent__ = self
        t.update()
        self._navlist = t.navlist
        self.table = t

    def template(self):
        # putting datefmt into request as the value provider for the
        # table currently uses it to determine output format...
        return self.table.render()

    def navlist(self):
        return self._navlist


class WorkspaceShortlog(WorkspaceLog):

    shortlog = True
    tbl = table.ShortlogTable
    label = 'Shortlog'


#class WorkspacePageShortlog(WorkspaceShortlog):
#    # for workspace main listing.
#
#    tbl = table.WorkspacePageShortlogTable
#

class WorkspaceLogRss(RssPage):

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

    clsobj = Workspace
    label = "Workspace Object Creation Form"

    @property
    def fields(self):
        settings = zope.component.getUtility(IPMR2GlobalSettings)
        if settings.workspace_idgen:
            return z3c.form.field.Fields(IWorkspace)

        return (z3c.form.field.Fields(IObjectIdMixin) +
            z3c.form.field.Fields(IWorkspace))

    def create(self, data):
        settings = zope.component.getUtility(IPMR2GlobalSettings)
        if settings.workspace_idgen:
            name = settings.workspace_idgen
            idgen = zope.component.queryUtility(IIdGenerator, name=name)
            if idgen is None:
                raise z3c.form.interfaces.ActionExecutionError(
                    ProcessingError(_('Cannot get id generator; please '
                        'contact the repository administrator.')))

            next_id = None
            if next_id in self.context or next_id is None:
                # generate next id
                next_id = idgen.next()
            data['id'] = next_id

        return super(WorkspaceAddForm, self).create(data)

    def add_data(self, ctxobj):
        ctxobj.title = self._data['title']
        ctxobj.description = self._data['description']
        ctxobj.storage = self._data['storage']


class WorkspaceStorageCreateForm(WorkspaceAddForm):
    """\
    Workspace add form.  This also creates the storage object.
    """

    label = "Create a New Workspace"

    @property
    def fields(self):
        settings = zope.component.getUtility(IPMR2GlobalSettings)
        if settings.workspace_idgen:
            return z3c.form.field.Fields(IWorkspace)

        # IWorkspaceStorageCreate has a validator attached to its id 
        # attribute to verify that the workspace id has not been taken.
        return (z3c.form.field.Fields(IWorkspaceStorageCreate) + 
            z3c.form.field.Fields(IWorkspace))

    def add_data(self, ctxobj):
        WorkspaceAddForm.add_data(self, ctxobj)
        storage = zope.component.getUtility(
            IStorageUtility, name=ctxobj.storage)
        storage.create(ctxobj)


class WorkspaceEditForm(form.EditForm):
    """\
    Workspace edit form.
    """

    fields = z3c.form.field.Fields(IWorkspace).omit('storage')
    label = "Workspace Edit Form"


class WorkspaceSyncFormBase(form.PostForm):
    """\
    The base sync form.
    """

    ignoreContext = True

    def _sync(self, external_uri):
        utility = zope.component.getUtility(
            IStorageUtility, name=self.context.storage)
        if not utility.validateExternalURI(external_uri):
            raise ValueError('`%s` is using a forbiddened protocol.' % 
                             external_uri)
        return utility.sync(self.context, external_uri)

    def sync(self, external_uri):
        try:
            result, msg = self._sync(external_uri)
        except Exception, e:
            self.status = u'Error syncing with %s: %s' % (
                external_uri, str(e))
            return

        if result:
            # redirect with message
            status = IStatusMessage(self.request)
            status.addStatusMessage(
                u'Successfully synced with %s.' % external_uri)
            if msg:
                status.addStatusMessage(msg)
            return self.request.response.redirect(self.context.absolute_url())

        self.status = u'Failure to sync.'


class WorkspaceSyncForm(WorkspaceSyncFormBase):
    """\
    Synchronize with data from another repository/workspace.
    """

    fields = z3c.form.field.Fields(IWorkspaceSync)

    @button.buttonAndHandler(u'Synchronize', name='syncWithTarget')
    def syncWithTarget(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        external_uri = data.get('external_uri', None)
        return self.sync(external_uri)


class WorkspaceForkForm(form.PostForm):
    """\
    Clone a remote workspace
    """

    label = u'Create personal fork of this workspace'
    ignoreContext = True

    @property
    def fields(self):
        settings = zope.component.getUtility(IPMR2GlobalSettings)
        if settings.workspace_idgen:
            return z3c.form.field.Fields()
        return z3c.form.field.Fields(IWorkspaceFork)

    def update(self):
        # manual role checking
        # This is needed because this form is anchored onto the target,
        # and anyone (authenticated) that could view this workspace
        # should be able to clone this.  This may change when we have a
        # specific permission setting to allow the viewing of this form.
        # For now, the default view permission is sufficient, but this
        # means anonymous users must be kicked out.
        pm = getToolByName(self.context, 'portal_membership')
        user = pm.getAuthenticatedMember()
        if pm.isAnonymousUser():
            # don't want to deal with anonymous non GETs
            raise Unauthorized()

        # set the id to the current value.
        if 'form.widgets.id' not in self.request:
            self.request['form.widgets.id'] = self.context.id

        return super(WorkspaceForkForm, self).update()

    @button.buttonAndHandler(u'Fork', name='fork')
    def forkWorkspace(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        self._data = data
        try:
            ctxobj = self.cloneToUserWorkspace()
        except Exception, e:
            # XXX failure could be anything. Log error?
            raise z3c.form.interfaces.ActionExecutionError(
                ProcessingError(str(e)))


        if ctxobj is not None:
            self.request.response.redirect(ctxobj.absolute_url())

    def cloneToUserWorkspace(self):
        settings = zope.component.getUtility(IPMR2GlobalSettings)
        target_root = settings.getCurrentUserWorkspaceContainer()

        if settings.workspace_idgen:
            name = settings.workspace_idgen
            idgen = zope.component.queryUtility(IIdGenerator, name=name)
            if idgen is None:
                raise ProcessingError(_('Cannot get id generator; please '
                        'contact the repository administrator.'))
            newid = idgen.next()
        else:
            newid = self._data['id']

        self._newid = newid

        if target_root is None:
            raise ProcessingError('User workspace container not found.')

        # 1. Create workspace object.
        if target_root.get(newid) is not None:
            raise ProcessingError('You already have a workspace with the '
                'same name, please try again with another name.')
        obj = Workspace(newid)
        target_root[newid] = obj
        ctxobj = target_root[newid]
        ctxobj.title = self.context.title
        ctxobj.description = self.context.description
        ctxobj.storage = self.context.storage

        # 2. Create the storage and synchronize it with context.
        utility = zope.component.getUtility(
            IStorageUtility, name=ctxobj.storage)
        utility.create(ctxobj)
        utility.syncWorkspace(ctxobj, self.context)

        return ctxobj


# Internal traverse views

class BaseFilePage(WorkspaceTraversePage):
    """\
    A Traversal Page that extracts and process the info when updated.
    Provides some properties that is available once that is done.
    """

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
    def downloadpath(self):
        """permanent download uri."""
        return '/'.join(self._getpath(view='download', path=self.data['file']))

    @property
    def viewpath(self):
        """view uri."""
        return '/'.join(self._getpath(view='file',
            path=self.data['file']))

    def absolute_url(self):
        return self.context.absolute_url()

    def update(self):
        pass

    def call_template(self):
        self.omit_index = True
        return self.__call__()


class FilePage(BaseFilePage):

    template = ViewPageTemplateFile('workspace_file_page.pt')
    label = ViewPageTemplateFile('workspace_file_label.pt')
    redirected = False

    def update(self):
        """\
        Acquire content from request_subpath from storage
        """

        storage = zope.component.getAdapter(self.context, IStorage)
        try:
            storage.checkout(self.request.get('rev', None))
        except RevisionNotFoundError:
            raise NotFound(self.context, self.context.title_or_id())

        request_subpath = self.request.get('request_subpath', [])

        try:
            data = storage.pathinfo('/'.join(request_subpath))
        except PathNotFoundError:
            # Only if really nothing is found.
            raise NotFound(self.context, self.context.title_or_id())

        # trigger subrepo dir if external is defined.
        if data['external']:
            # form the url # XXX this is based on the _subrepo format defined in
            # pmr2.mercurial - refer to test there because they are
            # the only users for now until a generic version of this
            # is implemented in the test storage.
            keys = data['external']
            keys['view'] = self.__name__ or 'rawfile'
            target = '%(location)s/%(view)s/%(rev)s/%(path)s' % keys
            self.redirected = True
            try:
                redir = self.request.response.redirect(target, trusted=True)
            except TypeError:
                # XXX wsgi response doesn't have trusted?
                redir = self.request.response.redirect(target)
            return redir

        # update rev using the storage rev
        self.request['rev'] = storage.rev
        self.request['shortrev'] = storage.shortrev
        # this is for rendering
        self.request['filepath'] = request_subpath or ['']
        # data
        self.request['_data'] = data
        self.request['_storage'] = storage

        self.request['enable_border'] = True

    def render(self):
        # We have to trigger the update methods of the providers before
        # we render the main template (self.index).  A naive way to
        # achieve this is to save the template result, and temporarily
        # redirect the template call to the rendered result.
        raw_template = self.template
        template_result = self.template()
        self.template = lambda: template_result
        result = super(FilePage, self).render()
        self.template = raw_template
        return result

    def __call__(self):
        self.update()
        if self.redirected:
            return u''
        return self.render()


class FileInfoPage(BaseFilePage):
    """\
    A Traversal Page that displays the pre-extracted info.
    """

    showinfo = True
    template = ViewPageTemplateFile('workspace_file_info.pt')

    def update(self):
        if not self.data['mimetype']():
            self.showinfo = False

    def render(self):
        if not self.showinfo:
            return ''
        return super(FileInfoPage, self).render()

    def __call__(self):
        return super(FileInfoPage, self).__call__()


class WorkspaceRawfile(FilePage):

    def render(self):
        data = self.request['_data']
        if data:
            # not supporting resuming download
            # XXX large files will eat RAM
            contents = data['contents']()

            if not isinstance(contents, basestring):
                # this is a rawfile view, this can be triggered by 
                # attempting to access a directory.  we redirect to the
                # standard file view.
                return self.request.response.redirect(self.viewpath)

            mimetype = data['mimetype']()
            # Force HTML to be served as plain text.
            if mimetype == 'text/html':
                # XXX this isn't enough to satiate MSIE fail, but...
                mimetype = 'text/plain'

            self.request.response.setHeader('Content-Type', mimetype)
            self.request.response.setHeader('Content-Length', data['size'])
            return contents
        else:
            raise NotFound(self.context, self.context.title_or_id())


class WorkspaceDownloadFile(WorkspaceRawfile):

    def render(self):
        data = self.request['_data']
        contents = super(WorkspaceDownloadFile, self).render()

        self.request.response.setHeader('Content-Disposition',
            'attachment; filename="%s"' % data['basename'])

        return contents


class WorkspaceRawfileXmlBase(WorkspaceRawfile):

    @property
    def xmlrooturi(self):
        """the root uri."""
        return '/'.join(self._getpath(view='xmlbase'))

    def render(self):
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

        data = WorkspaceRawfile.render(self)
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
