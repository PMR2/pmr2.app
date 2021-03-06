from sys import maxint
import cgi

import zope.component
import zope.interface
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.publisher.interfaces import NotFound

from z3c.form.interfaces import IForm

import z3c.table.column
import z3c.table.table
from z3c.table.value import ValuesMixin
from z3c.table.interfaces import ITable

from Products.CMFCore.utils import getToolByName

try:
    from pmr2.users.interfaces import IEmailManager
    _EMAIL_MANAGER = True
except ImportError:
    _EMAIL_MANAGER = False

from pmr2.app.workspace.exceptions import *
from pmr2.app.workspace.interfaces import IWorkspaceListing
from pmr2.app.workspace.interfaces import IStorage
from pmr2.app.workspace.i18n import MessageFactory as _


# Common

class ItemKeyColumn(z3c.table.column.Column):
    """\
    Column for selecting an item from a list or dictionary using a key.
    """

    itemkey = None
    errorValue = None

    def getItem(self, item):
        try:
            return item[self.itemkey]
        except:
            return self.errorValue

    def renderCell(self, item):
        result = self.getItem(item)

        if not isinstance(result, basestring):
            result = str(result)

        if not isinstance(result, unicode):
            # TODO maybe deal with UTF-16/32 eventually by checking for
            # the presence of BOM.
            try:
                result = result.decode('utf8')
            except UnicodeDecodeError:
                result = result.decode(self.fallback_encoding)

        return result


class ItemKeyRadioColumn(ItemKeyColumn, z3c.table.column.RadioColumn):

    def getItemKey(self, item):
        form = self.table.__parent__
        if not IForm.providedBy(form):
            return super(ItemKeyRadioColumn, self).getItemKey(item)
        try:
            result = form.widgets[self.__name__].name
        except KeyError:
            # XXX perhaps we have some sort of warning here as the form
            # does not define the widget we need, or that this column is
            # registered with a wrong name.
            result = super(ItemKeyRadioColumn, self).getItemKey(item)
        return result

    def getItemValue(self, item):
        return self.getItem(item)

    def renderCell(self, item):
        radio = z3c.table.column.RadioColumn.renderCell(self, item)
        return '<label>%s %s</label>' % (
            radio, self.getItem(item)[0:12]) # XXX improper shortrev


class EscapedItemKeyColumn(ItemKeyColumn):
    """With CGI escape."""

    fallback_encoding = 'latin1'

    def renderCell(self, item):
        result = super(EscapedItemKeyColumn, self).renderCell(item)
        return cgi.escape(result)


class ItemKeyReplaceColumn(ItemKeyColumn):
    """\
    Column for selecting an item, then replaced with replacement from a
    lookup table.
    """

    lookupTable = {}
    defaultValue = None

    def getItem(self, item):
        # not reusing getItem as it traps the exception on missing
        # key.
        try:
            result = item[self.itemkey]
        except:
            return self.errorValue
        return self.lookupTable.get(result, self.defaultValue)


# Workspace

class WorkspaceIdColumn(ItemKeyColumn):
    weight = 10
    header = _(u'Workspace ID')
    itemkey = 0


class WorkspaceStatusColumn(ItemKeyReplaceColumn):
    weight = 20
    itemkey = 1
    header = _(u'Object Status')
    lookupTable = {
        True: _(u'Valid'),
        False: _(u'Error'),
        None: _(u'Not Found'),
    }
    defaultValue = _(u'(unknown)')


class WorkspaceActionColumn(ItemKeyReplaceColumn):
    """
    The action column.  Will contain anchors to other forms and views.
    Those links are currently hard-coded.
    """

    weight = 30
    itemkey = 1
    header = _(u'Action')
    # XXX repository paths are assumed to be valid ids.
    lookupTable = {
        True: _(u'<a href="%s">[view]</a>'),
        False: _(u'<a href="@@workspace_object_info?%s">[more info]</a>'),
        None: _(u'<a href="@@workspace_object_create?form.widgets.id=%s">'
                 '[create]</a>'),
    }
    defaultValue = _(u'(unknown)')

    def renderCell(self, item):
        # create anchors to actual object if valid
        # create anchors to workspace creation form if not found
        # do something else if error
        result = self.getItem(item)
        if result:
            result = result % item[0]
        return result


class IWorkspaceStatusTable(ITable):
    """
    Marker interface for workspace status table.
    """


class WorkspaceStatusTable(z3c.table.table.Table):

    zope.interface.implements(IWorkspaceStatusTable)

    def absolute_url(self):
        return self.request.getURL()


class ValuesForWorkspaceStatusTable(ValuesMixin):
    """Values from a simple IContainer."""

    zope.component.adapts(zope.interface.Interface, IBrowserRequest,
        IWorkspaceStatusTable)

    @property
    def values(self):
        listing = zope.component.getAdapter(self.context, IWorkspaceListing)
        return listing()

# Workspace log table.


class ChangesetRadioColumn(ItemKeyRadioColumn):
    weight = 0
    header = _(u'Changeset')
    itemkey = 'node'


class ChangesetDateColumn(ItemKeyColumn):
    weight = 10
    header = _(u'Date')
    itemkey = 'date'


class ChangesetAuthorColumn(EscapedItemKeyColumn):
    weight = 20
    header = _(u'Author')
    itemkey = 'author'


class ChangesetAuthorEmailColumn(EscapedItemKeyColumn):
    weight = 21
    header = _(u'Author')
    itemkey = 'author'

    def renderCell(self, item):
        author = None
        portal = None
        name = super(ChangesetAuthorEmailColumn, self).renderCell(item)
        email = item.get('email')
        portal_url = getToolByName(self.context, 'portal_url', None)
        pm = getToolByName(self.context, 'portal_membership', None)

        if portal_url:
            portal = portal_url.getPortalObject()

        if pm and portal:
            # find the latest user.
            user = sorted(pm.searchForMembers(name=name, email=email),
                lambda x, y: x.getProperty('last_login_time', '') <
                    y.getProperty('last_login_time', ''))
            if user:
                author = user[0].getUserName()

        if portal and not author and _EMAIL_MANAGER:
            # last ditch effort
            eman = zope.component.queryAdapter(portal, IEmailManager)
            if eman:
                author = eman.get_login_for(email)

        if not author:
            return name

        href = portal.absolute_url() + '/author/' + author

        return '<a href="%s">%s</a>' % (href, name)


class ChangesetDescColumn(EscapedItemKeyColumn):
    weight = 30
    header = _(u'Log')
    itemkey = 'desc'


class ShortlogOptionColumn(ItemKeyColumn):
    weight = 40
    header = _(u'Options')
    itemkey = 'node'

    def archive_options(self, item):
        # Return links to acquire the archive of each revision.
        try:
            storage = zope.component.queryAdapter(self.context, IStorage)
        except ValueError:
            # the source form should have failed to render anyway...
            # unless this was part of a test.  Ignore this error.
            return []
        formats = storage.archiveFormats
        # XXX configuration for disabling archive types isn't created;
        # magic here.
        disabled = ['tar',]

        return [u'<a href="%s/@@archive/%s/%s">[%s]</a>' % (
            self.context.absolute_url(), self.getItem(item), format, format,)
            for format in formats if format not in disabled
        ]

    def renderCell(self, item):
        result = [
            u'<a href="%s/@@file/%s/">[files]</a>' % \
                (self.context.absolute_url(), self.getItem(item)),
        ]
        # should render changeset link for diffs and other types once a
        # more generic version of the option column is implemented
        # alongside with archive options
        result.extend(self.archive_options(item))
        return '\n'.join(result)


class IChangelogTable(ITable):
    """\
    The changelog table.
    """

    def __init__(self, *a, **kw):
        self.navlist = []


class ChangelogTable(z3c.table.table.Table):

    zope.interface.implements(IChangelogTable)
    sortOn = None


class IShortlogTable(ITable):
    """\
    The changelog table.
    """


class ShortlogTable(z3c.table.table.Table):

    zope.interface.implements(IChangelogTable, IShortlogTable)
    sortOn = None


class ValuesForChangelogTable(ValuesMixin):
    """Values from a simple IContainer."""

    filter_keys = ['author', 'email', 'date', 'node', 'rev', 'desc',]

    zope.component.adapts(zope.interface.Interface, IBrowserRequest,
        IChangelogTable)

    # will benefit @instance.memoize instead?
    # can be difficult to combine this with existing work...
    @property
    def values(self):
        # filter the values
        # return this as a list since the whole thing will be rendered.
        def clean(d):
            return dict([i for i in d.items() if i[0] in self.filter_keys])
        return [clean(d) for d in self.log()]

    def log(self):
        try:
            storage = zope.component.queryAdapter(self.context, IStorage)
            datefmt = self.request.get('datefmt', None)
            rev = self.request.get('rev', None)
            shortlog = self.request.get('shortlog', False)
            maxchanges = self.request.get('maxchanges', 50)
            if datefmt:
                storage.datefmt = datefmt
            # This might be worth fixing, since the purpose here is
            # to resolve the full revision id from user input.
            if rev:
                storage.checkout(rev)
            rev = storage.rev
            logs = storage.log(rev, maxchanges, shortlog=shortlog)
            self.table.navlist = storage.lastnav
            return logs
        except RevisionNotFoundError:
            raise NotFound(self.context, self.context.title_or_id())


# Workspace manifest table.

class FilePermissionColumn(EscapedItemKeyColumn):
    weight = 10
    header = _(u'Permissions')
    itemkey = 'permissions'


class FileDatetimeColumn(EscapedItemKeyColumn):
    weight = 20
    header = _(u'Date')
    itemkey = 'date'
    defaultValue = u''
    errorValue = u''


class FileSizeColumn(EscapedItemKeyColumn):
    weight = 15
    header = _(u'Size')
    itemkey = 'size'
    defaultValue = u''
    errorValue = u''


class FilenameColumn(EscapedItemKeyColumn):
    weight = 10
    header = _(u'Filename')
    itemkey = 'basename'

    def renderCell(self, item):
        return (u'<span><i class="icon-%s"></i> %s</span>' % (
            item['contenttype'],
            self.getItem(item),
        ))


class FilenameColumnLinked(EscapedItemKeyColumn):
    weight = 11
    header = _(u'Filename')
    itemkey = 'basename'

    def renderCell(self, item):
        if item['fullpath']:
            # XXX this is an override for embedded workspaces, better 
            # solution may be required.
            href = item['fullpath']
        else:
            href = '/'.join((
                self.table.context.absolute_url(),
                item['baseview'],
                item['node'],
                item['file'],
            ))

        datasrc = ''
        csscls = 'wsfmenu open'
        if item['permissions'][0] == '-':
            csscls = 'wsfmenu download'
            datasrc = ' data-src="%s"' % '/'.join((
                self.table.context.absolute_url(),
                '@@download',
                item['node'],
                item['file'],
            ))

        return (u'<span class="%s"><a href="%s"%s><i class="icon-%s"></i> '
                '%s</a></span>' % (
            csscls,
            href,
            datasrc,
            item['contenttype'],
            self.getItem(item),
        ))


class FileOptionColumn(EscapedItemKeyColumn):
    weight = 50
    header = _(u'Options')
    itemkey = 'basename'
    _browse = True
    _download = False

    def renderCell(self, item):
        result = []

        if self._browse:
            # XXX this is an override for embedded workspaces, better 
            # solution may be required.
            if item['fullpath']:
                result.append(u'<a href="%s">[%s]</a>' % (
                    item['fullpath'],
                    _(u'browse'),
                ))
            else:
                result.append(u'<a href="%s/%s/%s/%s">[%s]</a>' % (
                    self.table.context.absolute_url(),
                    item['baseview'],
                    item['node'],
                    item['file'],
                    _(u'browse'),
                ))

        if item['permissions'][0] == '-':
            if self._download:
                result.append(u'<a href="%s/@@rawfile/%s/%s">[%s]</a>' % (
                    self.table.context.absolute_url(),
                    item['node'],
                    item['file'],
                    _(u'download'),
                ))

            # XXX *.session.xml assumption
            # XXX make this query some sort of utility or adapter and
            # *.session.xml assumption
            if item['file'].endswith('.session.xml'):
                result.append(u'<a href="%s/@@xmlbase/%s/%s">[%s]</a>' % (
                    self.table.context.absolute_url(),
                    item['node'],
                    item['file'],
                    _(u'run'),
                ))

        return ' '.join(result)



class IFileManifestTable(ITable):
    """\
    The file manifest table.
    """


class FileManifestTable(z3c.table.table.Table):

    zope.interface.implements(IFileManifestTable)

    sortOn = None
    startBatchingAt = maxint
    cssClasses = {'table': 'workspace-manifest listing'}
