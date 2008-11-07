import z3c.table.column
import z3c.table.table

from zope.i18nmessageid import MessageFactory
_ = MessageFactory("pmr2")


class WorkspaceIdColumn(z3c.table.column.Column):
    weight = 10
    header = _(u'Workspace ID')

    def renderCell(self, item):
        return u'%s' % item[0]


class WorkspaceStatusColumn(z3c.table.column.Column):
    weight = 20
    header = _(u'Object Status')
    _values = {
        True: _(u'Valid'),
        False: _(u'Error'),
        None: _(u'Not Found'),
    }

    def renderCell(self, item):
        return u'%s' % self._values.get(item[1], _(u'(unknown)'))


class WorkspaceStatusTable(z3c.table.table.SequenceTable):

   def setUpColumns(self):
        return [
            z3c.table.column.addColumn(
                self, WorkspaceIdColumn, u'workspace_id'
            ),
            z3c.table.column.addColumn(
                self, WorkspaceStatusColumn, u'workspace_status'
            ),
        ]

