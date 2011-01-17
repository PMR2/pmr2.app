import zope.interface
from Products.CMFCore.utils import getToolByName
from zope.i18nmessageid import MessageFactory
_ = MessageFactory("pmr2")

from pmr2.app.workspace.table import ItemKeyColumn
from pmr2.app.workspace.table import ItemKeyRadioColumn

from pmr2.app.workspace.table import IShortlogTable
from pmr2.app.workspace.table import ShortlogTable


class ExposureColumn(ItemKeyColumn):
    weight = 50
    header = _(u'Exposure')
    itemkey = None  # actually derived from catalog

    def getItem(self, item):
        workspace = self.context
        pt = getToolByName(workspace, 'portal_catalog', None)
        if pt is None:
            return None
        query = {}
        query['portal_type'] = 'Exposure'  # XXX this may need changing
        query['pmr2_exposure_workspace'] = [
            workspace.id,
            u'/'.join(workspace.getPhysicalPath()),
        ]
        query['pmr2_exposure_commit_id'] = item['node']
        return pt(**query)

    def getItemValue(self, item):
        # return the object path of the exposure
        return [i.getPath() for i in self.getItem(item)]

    def renderCell(self, item):
        items = self.getItem(item)
        if items:
            return u'<br />\n'.join([
                u'<a class="state-%s" href="%s">%s</a>' % (i.pmr2_review_state, 
                i.getURL(), i.Title or i.id) for i in items
            ])
        return u''


class ExposureRadioColumn(ExposureColumn, ItemKeyRadioColumn):
    """\
    This combines the exposure column with the radio column, but as this
    column provides multiple values at a time, this is different from
    the shipped RadioColumn.
    """

    _selectedItems = None

    @apply
    def selectedItem():
        # do not use the table, because a) this column isn't a primary
        # key, b) this column provides multiple values per cell, and
        # c) the primary key lives in another column.
        def get(self):
            if self._selectedItems and len(self._selectedItems):
                return list(self._selectedItems).pop()
        def set(self, value):
            self._selectedItems = [value]
        return property(get, set)

    def update(self):
        """\
        Like the parent method, this figures out the selectedItem, but
        we won't be using self.table.values as the column provides it.
        """

        # using None as the parameter value as getItemKey should return
        # the same result regardless of input.
        selected = self.request.get(self.getItemKey(None), [])
        if selected:
            self.selectedItem = selected.pop()

    def renderCell(self, item):
        items = self.getItem(item)
        if not items:
            return u'(none)'
        result = []
        for i in items:
            selected = (i.getPath() == self.selectedItem) and \
                u'checked="checked"' or u''
            radio = u'<input type="radio" class="%s" name="%s" ' \
                     'value="%s" %s />' % ('radio-widget',
                                           self.getItemKey(item), 
                                           i.getPath(),
                                           selected)
            result.append(u'<label>%s <a class="state-%s" '
                           'href="%s">%s</a></label>' % (
                radio, i.pmr2_review_state, i.getURL(), i.Title or i.id))
        return '<br />\n'.join(result)


class IExposureRolloverLogTable(IShortlogTable):
    """Exposure rollover table"""


class ExposureRolloverLogTable(ShortlogTable):

    zope.interface.implements(IExposureRolloverLogTable)
    sortOn = None
