from sys import maxint
import cgi

import zope.component
import zope.interface
from zope.publisher.interfaces.browser import IBrowserRequest

from z3c.form.interfaces import IForm

import z3c.table.column
import z3c.table.table
from z3c.table.value import ValuesMixin
from z3c.table.interfaces import ITable

from zope.i18nmessageid import MessageFactory
_ = MessageFactory("pmr2")

from pmr2.app.workspace.exceptions import *
from pmr2.app.workspace.interfaces import IWorkspaceListing
from pmr2.app.workspace.interfaces import IStorage


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
        return self.getItem(item)


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

    def renderCell(self, item):
        result = self.getItem(item)
        try:
            result = unicode(result)
        except UnicodeDecodeError:
            # XXX magic default codec
            result = unicode(result, 'latin1')
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


class ChangesetDescColumn(EscapedItemKeyColumn):
    weight = 30
    header = _(u'Log')
    itemkey = 'desc'


class ShortlogOptionColumn(ItemKeyColumn):
    weight = 40
    header = _(u'Options')
    itemkey = 'node'

    def renderCell(self, item):
        # also could render changeset link (for diffs)
        result = [
            u'<a href="%s/@@file/%s/">[manifest]</a>' % \
                (self.context.absolute_url(), self.getItem(item)),
            u'<a href="%s/@@archive/%s/zip">[zip]</a>' % \
                (self.context.absolute_url(), self.getItem(item)),
            u'<a href="%s/@@archive/%s/gz">[gz]</a>' % \
                (self.context.absolute_url(), self.getItem(item)),
        ]
        return ' '.join(result)


class IChangelogTable(ITable):
    """\
    The changelog table.
    """


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

    zope.component.adapts(zope.interface.Interface, IBrowserRequest,
        IChangelogTable)

    @property
    def values(self):
        # XXX because z3c.tables does not support iterators.
        return list(self.log())

    def log(self):
        try:
            storage = zope.component.queryAdapter(self.context, IStorage)
            datefmt = self.request.get('datefmt', None)
            rev = self.request.get('rev', None)
            maxchanges = self.request.get('maxchanges', 50)
            if datefmt:
                storage.datefmt = datefmt
            # This might be worth fixing, since the purpose here is
            # to resolve the full revision id from user input.
            if rev:
                storage.checkout(rev)
            rev = storage.rev
            return storage.log(rev, maxchanges)
        except RevisionNotFoundError:
            raise HTTPNotFound(self.context.title_or_id())


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
    weight = 30
    header = _(u'Size')
    itemkey = 'size'
    defaultValue = u''
    errorValue = u''


class FilenameColumn(EscapedItemKeyColumn):
    weight = 40
    header = _(u'Filename')
    itemkey = 'basename'

    def renderCell(self, item):
        # also could render changeset link (for diffs)
        return u'<a href="%s/@@file/%s/%s">%s</a>' % (
            self.table.context.absolute_url(),
            item['node'],
            item['file'],
            self.getItem(item),
        )


class FileOptionColumn(EscapedItemKeyColumn):
    weight = 50
    header = _(u'Options')
    itemkey = 'basename'

    def renderCell(self, item):
        # also could render changeset link (for diffs)
        if item['permissions'][0] != 'd':
            result = [u'<a href="%s/@@rawfile/%s/%s">[%s]</a>' % (
                self.table.context.absolute_url(),
                item['node'],
                item['file'],
                _(u'download'),
            )]

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
        else:
            return u''



class IFileManifestTable(ITable):
    """\
    The file manifest table.
    """


class FileManifestTable(z3c.table.table.Table):

    zope.interface.implements(IFileManifestTable)

    sortOn = None
    startBatchingAt = maxint
