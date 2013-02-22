import zope.component
from zope.publisher.interfaces import NotFound

from pmr2.app.settings.interfaces import IPMR2GlobalSettings
from pmr2.app.settings.browser.dashboard import DashboardOption

from pmr2.app.workspace.browser.templates import ViewPageTemplateFile, path


# May want to consider figuring out how to integrate this with the Plone
# portal_actions, if applicable.

class WorkspaceDashboardOption(DashboardOption):

    template = ViewPageTemplateFile(path('no_default_container.pt'))

    def getTargetContainer(self):
        """
        Returns the workspace container as determined by the settings.
        """

        settings = zope.component.getUtility(IPMR2GlobalSettings)

        if settings.create_user_workspace:
            uwc = settings.getCurrentUserWorkspaceContainer()
            if uwc is not None:
                return uwc

        # Otherwise return the global workspace container.
        target = settings.getWorkspaceContainer()
        if target is None:
            raise NotFound(self.context, settings.default_workspace_subpath)
        return target

    def getTarget(self, path=None):
        target = self.getTargetContainer().absolute_url()
        return '/'.join([target, path or ''])


class WorkspaceHome(WorkspaceDashboardOption):

    title = 'List personal workspaces'


class WorkspaceAdd(WorkspaceDashboardOption):

    title = 'Create personal workspace'
    path = '+/addWorkspace'
