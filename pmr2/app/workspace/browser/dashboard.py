import zope.component

from pmr2.app.settings.interfaces import IPMR2GlobalSettings
from pmr2.app.settings.browser.dashboard import DashboardOption

from pmr2.app.workspace.browser.templates import ViewPageTemplateFile, path


# May want to consider figuring out how to integrate this with the Plone
# portal_actions, if applicable.

class WorkspaceDashboardOption(DashboardOption):

    template = ViewPageTemplateFile(path('no_default_container.pt'))

    def getTarget(self, path=None):
        settings = zope.component.getUtility(IPMR2GlobalSettings)
        uwc = settings.getCurrentUserWorkspaceContainer()

        if uwc is not None:
            target = uwc.absolute_url()
            return '/'.join([target, path or ''])
        return None


class WorkspaceHome(WorkspaceDashboardOption):

    title = 'List personal workspaces'


class WorkspaceAdd(WorkspaceDashboardOption):

    title = 'Create personal workspace'
    path = '+/addWorkspace'
