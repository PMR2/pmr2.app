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


class ShortlogOptionColumn(z3c.table.column.Column):
    weight = 40
    header = _(u'Options')

    def renderCell(self, item):
        return u'[placeholder]'


class ChangelogTable(z3c.table.table.SequenceTable):

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


class ShortlogTable(z3c.table.table.SequenceTable):

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

