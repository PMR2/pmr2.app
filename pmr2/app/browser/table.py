import cgi

import z3c.table.column
import z3c.table.table

from zope.i18nmessageid import MessageFactory
_ = MessageFactory("pmr2")


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


class WorkspaceStatusTable(z3c.table.table.SequenceTable):

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


# Workspace log table.

class ChangesetDateColumn(ItemKeyColumn):
    weight = 10
    header = _(u'Changeset Date')
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
        return u'<a href="%s/@@file/%s/">[manifest]</a>' % \
            (self.context.context.absolute_url(), self.getItem(item))


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
