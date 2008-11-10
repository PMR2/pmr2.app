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
        # create anchors to actual object if valid
        # create anchors to workspace creation form if not found
        # do something else if error
        return u'%s' % self._values.get(item[1], _(u'(unknown)'))


class WorkspaceActionColumn(z3c.table.column.Column):
    """
    The action column.  Will contain anchors to other forms and views.
    Those links are currently hard-coded.
    """

    weight = 30
    header = _(u'Action')
    # XXX repository paths are assumed to be valid ids.
    _values = {
        True: _(u'<a href="%s">[view]</a>'),
        False: _(u'<a href="@@workspace_object_info?%s">[more info]</a>'),
        None: _(u'<a href="@@workspace_object_create?form.widgets.id=%s">'
                 '[create]</a>'),
    }

    def renderCell(self, item):
        # create anchors to actual object if valid
        # create anchors to workspace creation form if not found
        # do something else if error
        result = self._values.get(item[1], u'')
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

