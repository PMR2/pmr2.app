from zope.interface import implements

from plone.app.contentmenu.menu import WorkflowSubMenuItem
from plone.app.contentmenu.view import ContentMenuProvider
from plone.app.contentmenu.interfaces import IWorkflowSubMenuItem


class WorkspaceMenuProvider(ContentMenuProvider):
    """\
    This is a custom menu provider for workspaces.

    For simplicity in these early stages, we just calculate and return
    some hard-coded list, instead of defining all the adapters,
    interfaces and xml to generate these simple menues.
    """

    def menu(self):
        """\
        This is a method with magic values.  The entire menu is rather
        hard coded, values assumed.  These basically need to be
        built from querying adapters or what not.
        """

        rev = self.view.view.form_instance.rev
        workspace = self.context.id
        queryStr = '%s/@@create?type=%s&workspace=%s&rev=%s'

        actionRootUri = self.context.absolute_url()
        mkSandboxUri = queryStr % (actionRootUri, 'sandbox', workspace, rev)
        mkExposureUri = queryStr % (actionRootUri, 'exposure', workspace, rev)

        items = [{
            'title': u'Workspace Actions',
            'action': actionRootUri,
            'description': u'Workspace Actions',
            'extra': {
                'id': 'workspace-exposure-actions',
            },
            'icon': None,
            'selected': u'',
            'submenu': [

                {
                    'title': 'Create Sandbox',
                    'action': mkSandboxUri,
                    'description': 'Creates a Sandbox from this Workspace.',
                    'extra': {
                        'class': 'kssIgnore',
                        'id': 'create-sandbox',
                        'separator': None
                    },
                    'icon': None,
                    'selected': False,
                    'submenu': None,
                },

                {
                    'title': 'Create Exposure',
                    'action': mkExposureUri,
                    'description': 'Creates an Exposure of this revision of this Workspace.',
                    'extra': {
                        'class': 'kssIgnore',
                        'id': 'create-exposure',
                        'separator': None
                    },
                    'icon': None,
                    'selected': False,
                    'submenu': None,
                },

            ],
        }]

        return items
