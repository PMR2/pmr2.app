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
        workspace = self.context.context  # the workspace
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

    def renderCell(self, item):
        items = self.getItem(item)
        if items:
            return u'<br />\n'.join([
                u'<a class="state-%s" href="%s">%s</a>' % (i.pmr2_review_state, 
                i.getURL(), i.Title or i.id) for i in items
            ])
        return u''


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


class IExposureRolloverLogTable(IShortlogTable):
    """Exposure rollover table"""


class ExposureRolloverLogTable(ShortlogTable):

    zope.interface.implements(IExposureRolloverLogTable)
    sortOn = None
