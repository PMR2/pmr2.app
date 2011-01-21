import urllib

import zope.component
import zope.interface

from zope.app.publisher.interfaces.browser import IBrowserMenu
from zope.app.publisher.browser.menu import BrowserSubMenuItem
from zope.app.publisher.browser.menu import BrowserMenu

from plone.app.contentmenu.view import ContentMenuProvider
from pmr2.app.workspace.interfaces import IStorage
from pmr2.app.workspace.interfaces import IFileMenu
from pmr2.app.workspace.interfaces import IFileSubMenuItem
from pmr2.app.workspace.interfaces import IWorkspaceFileUtility


class WorkspaceMenuProvider(ContentMenuProvider):
    """\
    This is a custom menu provider for workspaces.

    For simplicity in these early stages, we just calculate and return
    some hard-coded list, instead of defining all the adapters,
    interfaces and xml to generate these simple menues.
    """

    def menu(self):
        menu = zope.component.getUtility(
            IBrowserMenu, name='pmr2_workspacemenu')
        items = menu.getMenuItems(self.context, self.request)
        items.reverse()
        return items


class FileSubMenuItem(BrowserSubMenuItem):
    zope.interface.implements(IFileSubMenuItem)

    title = 'Workspace Actions'  # File View
    description = 'Actions for the current workspace'
    submenuId = 'pmr2_workspacemenu_file'

    order = 60
    extra = {'id': 'pmr2-workspacemenu-file'}

    def __init__(self, context, request):
        BrowserSubMenuItem.__init__(self, context, request)
        self.context_state = zope.component.getMultiAdapter((context, request),
            name='plone_context_state')

    def getToolByName(self, tool):
        return getToolByName(getSite(), tool)

    @property
    def action(self):
        # XXX should be a disambiguation page
        return self.context.absolute_url()  # + '/workspace_actions'

    def available(self):
        return True

    def selected(self):
        return False


class FileMenu(BrowserMenu):
    zope.interface.implements(IFileMenu)

    def getMenuItems(self, context, request):

        # request should already have rev and path populated.
        storage = zope.component.getAdapter(context, IStorage)
        # however we still want the canonical revision identifier.
        storage.checkout(request['rev'])

        rev = storage.rev
        workspace = context.id
        path = '/'.join(request['filepath'])

        if not rev:
            # invalid revision; no available action.
            return []

        menus = zope.component.getUtilitiesFor(IWorkspaceFileUtility)
        items = []

        for id_, m in menus:
            action = '%s/@@%s/%s/%s' % (
                context.absolute_url(), m.view, rev, path)
            items.append({
                'title': m.title,
                'action': action,
                'description': m.description,
                'extra': {
                    'class': 'kssIgnore',
                    'id': id_,
                    'separator': None,
                },
                'icon': None,
                'selected': False,
                'submenu': None,
            })

        return items
