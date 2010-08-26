from sys import maxint
import cgi

import zope.component
import zope.interface
from zope.publisher.interfaces.browser import IBrowserRequest
from Products.CMFCore.utils import getToolByName

import z3c.table.column
import z3c.table.table
from z3c.table.value import ValuesMixin
from z3c.table.interfaces import ITable

from zope.i18nmessageid import MessageFactory
_ = MessageFactory("pmr2")

from pmr2.app.workspace.interfaces import IWorkspaceListing


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

    def getItemValue(self, item):
        return self.getItem(item)

    def renderCell(self, item):
        radio = z3c.table.column.RadioColumn.renderCell(self, item)
        return '<label>%s %s</label>' % (
            radio, self.getItem(item)[0:12])


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

    def setUpColumns(self):
        return [
            z3c.table.column.addColumn(
                self, WorkspaceIdColumn, u'workspace_id'
            ),
            z3c.table.column.addColumn(
                self, WorkspaceStatusColumn, u'workspace_status'
            ),
            z3c.table.column.addColumn(
                self, WorkspaceActionColumn, u'workspace_action'
            ),
        ]

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

    def getItemKey(self, item):
        # XXX magic
        return u'form.widgets.commit_id'


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
                (self.context.context.absolute_url(), self.getItem(item)),
            u'<a href="%s/@@archive/%s/zip">[zip]</a>' % \
                (self.context.context.absolute_url(), self.getItem(item)),
            u'<a href="%s/@@archive/%s/gz">[gz]</a>' % \
                (self.context.context.absolute_url(), self.getItem(item)),
        ]
        return ' '.join(result)


class ExposureColumn(ItemKeyColumn):
    weight = 50
    header = _(u'Exposure')
    itemkey = None  # actually derived from catalog

    def getItem(self, item):
        workspace = self.context.context  # the workspace
        pt = getToolByName(workspace, 'portal_catalog')
        query = {}
        query['portal_type'] = 'Exposure'  # XXX this may need changing
        query['pmr2_exposure_workspace'] = [
            workspace.id,
            u'/'.join(workspace.getPhysicalPath()),
        ]
        query['pmr2_exposure_commit_id'] = item['node']
        return pt(**query)

    def renderCell(self, item):
        items = self.getItem(item)
        if items:
            return u'<br />\n'.join([
                u'<a class="state-%s" href="%s">%s</a>' % (i.pmr2_review_state, 
                i.getURL(), i.Title or i.id) for i in items
            ])
        return u'(none)'


class ExposureRadioColumn(ItemKeyRadioColumn, ExposureColumn):

    def getItemKey(self, item):
        # XXX magic
        return u'form.widgets.exposure_id'

    def renderCell(self, item):
        items = self.getItem(item)
        if not items:
            return u'(none)'
        result = []
        for i in items:
            selected = (item == self.selectedItem) and \
                u'checked="checked"' or u''
            radio = u'<input type="radio" class="%s" name="%s" ' \
                     'value="%s" %s />' % ('radio-widget',
                                           self.getItemKey(item), 
                                           i.id,
                                           selected)
            result.append(u'<label>%s <a href="%s">%s</a></label>' % (
                radio, i.getURL(), i.Title or i.id))
        return '<br />\n'.join(result)


class ChangelogTable(z3c.table.table.Table):

    sortOn = None

    def setUpColumns(self):
        return [
            z3c.table.column.addColumn(
                self, ChangesetDateColumn, u'changeset_date'
            ),
            z3c.table.column.addColumn(
                self, ChangesetAuthorColumn, u'changeset_author'
            ),
            z3c.table.column.addColumn(
                self, ChangesetDescColumn, u'changeset_desc'
            ),
        ]


class ShortlogTable(z3c.table.table.Table):

    sortOn = None

    def setUpColumns(self):
        return [
            z3c.table.column.addColumn(
                self, ChangesetDateColumn, u'changeset_date'
            ),
            z3c.table.column.addColumn(
                self, ChangesetAuthorColumn, u'changeset_author'
            ),
            z3c.table.column.addColumn(
                self, ChangesetDescColumn, u'changeset_desc'
            ),
            z3c.table.column.addColumn(
                self, ShortlogOptionColumn, u'shortlog_opt'
            ),
        ]


class WorkspacePageShortlogTable(z3c.table.table.Table):

    sortOn = None

    def setUpColumns(self):
        return [
            z3c.table.column.addColumn(
                self, ChangesetDateColumn, u'changeset_date'
            ),
            z3c.table.column.addColumn(
                self, ChangesetAuthorColumn, u'changeset_author'
            ),
            z3c.table.column.addColumn(
                self, ChangesetDescColumn, u'changeset_desc'
            ),
            z3c.table.column.addColumn(
                self, ShortlogOptionColumn, u'shortlog_opt'
            ),
            z3c.table.column.addColumn(
                self, ExposureColumn, u'exposure_list'
            ),
        ]


class ExposureRolloverLogTable(z3c.table.table.Table):

    sortOn = None

    def setUpColumns(self):
        return [
            z3c.table.column.addColumn(
                self, ChangesetRadioColumn, u'node'
            ),
            z3c.table.column.addColumn(
                self, ChangesetDateColumn, u'changeset_date'
            ),
            z3c.table.column.addColumn(
                self, ChangesetAuthorColumn, u'changeset_author'
            ),
            z3c.table.column.addColumn(
                self, ChangesetDescColumn, u'changeset_desc'
            ),
            z3c.table.column.addColumn(
                self, ShortlogOptionColumn, u'shortlog_opt'
            ),
            z3c.table.column.addColumn(
                self, ExposureRadioColumn, u'exposure_list'
            ),
        ]

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
            self.table.context.context.absolute_url(),
            self.table.context.storage.rev,
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
                self.table.context.context.absolute_url(),
                self.table.context.storage.rev,
                item['file'],
                _(u'download'),
            )]

            # *.session.xml assumption
            if item['file'].endswith('.session.xml'):
                result.append(u'<a href="%s/@@xmlbase/%s/%s">[%s]</a>' % (
                    self.table.context.context.absolute_url(),
                    self.table.context.storage.rev,
                    item['file'],
                    _(u'run'),
                ))

            return ' '.join(result)
        else:
            return u''


class FileManifestTable(z3c.table.table.Table):

    sortOn = None
    startBatchingAt = maxint

    def setUpColumns(self):
        return [
            z3c.table.column.addColumn(
                self, FilePermissionColumn, u'file_perm'
            ),
            z3c.table.column.addColumn(
                self, FilenameColumn, u'file_name'
            ),
            z3c.table.column.addColumn(
                self, FileDatetimeColumn, u'file_datetime'
            ),
            z3c.table.column.addColumn(
                self, FileSizeColumn, u'file_size'
            ),
            z3c.table.column.addColumn(
                self, FileOptionColumn, u'file_opt'
            ),
        ]
