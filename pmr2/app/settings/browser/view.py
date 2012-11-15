import zope.component

from pmr2.z3cform import page

from pmr2.app.settings.interfaces import IPMR2GlobalSettings
from pmr2.app.settings.browser.templates import path, ViewPageTemplateFile


class DashboardView(page.SimplePage):

    template = ViewPageTemplateFile(path('pmr2_info.pt'))

    def actions(self):
        # XXX replace this with an adapter that captures all the pages
        # made available to this view.
        return [
            {
                'href': '/'.join([self.__name__, 'workspace-home']),
                'label': 'Personal workspaces',
            }
        ]


# XXX consider moving some of these to be under pmr2.app.workspace.

class WorkspaceDashboardPage(page.SimplePage):

    template = ViewPageTemplateFile(path('no_default_container.pt'))
    title = ''
    # the action subpath within the target workspace.
    path = None

    def getTarget(self, path=None):
        settings = zope.component.getUtility(IPMR2GlobalSettings)
        uwc = settings.getCurrentUserWorkspaceContainer()

        if uwc is not None:
            target = uwc.absolute_url()
            return '/'.join([target, path or ''])
        return None

    def __call__(self):
        target = self.getTarget(self.path)
        if target:
            return self.request.response.redirect(target)
        return super(WorkspaceHomeView, self).__call__()


class WorkspaceHomePage(WorkspaceDashboardPage):

    title = 'Personal workspaces'


class WorkspaceAddPage(WorkspaceDashboardPage):

    title = 'Add workspace'
    path = '+/addWorkspace'
