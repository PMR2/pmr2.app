import zope.component
import zope.interface

from pmr2.z3cform import page

from pmr2.app.settings.interfaces import IDashboard, IDashboardOption
from pmr2.app.settings.browser.templates import path, ViewPageTemplateFile


class Dashboard(page.SimplePage):

    zope.interface.implements(IDashboard)

    template = ViewPageTemplateFile(path('pmr2_info.pt'))

    def actions(self):
        options = zope.component.getAdapters(
            (self, self.request), IDashboardOption)

        result = [{
                'action': '/'.join([
                    self.context.absolute_url(), self.__name__, id]),
                'label': option.title,
                'id': 'pmr2-dashboard-' + id,
            } for id, option in options]
        return result


class DashboardOption(page.SimplePage):

    zope.interface.implements(IDashboardOption)

    title = None
    # the action subpath within the target option
    path = None

    def getTarget(self, path=None):
        raise NotImplementedError

    def __call__(self):
        target = self.getTarget(self.path)
        if target:
            return self.request.response.redirect(target)
        return super(DashboardOption, self).__call__()
