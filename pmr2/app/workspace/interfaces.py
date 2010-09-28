import zope.interface
import zope.schema

from pmr2.app.schema import ObjectId

from zope.app.publisher.interfaces.browser import IBrowserMenu
from zope.app.publisher.interfaces.browser import IBrowserSubMenuItem
from zope.app.publisher.interfaces.browser import IMenuItemType


class IStorage(zope.interface.Interface):
    """
    Storage class.  Provides the methods to access data behind a 
    workspace.
    """


class IStorageUtility(zope.interface.Interface):
    """\
    Storage utility.  Used to initialize a storage object from a
    workspace.
    """

    title = zope.schema.TextLine(
        title=u'Title',
        default=u'Workspace',
    )


# content

class IWorkspaceContainer(zope.interface.Interface):
    """\
    Container for the model workspaces.
    """

    title = zope.schema.TextLine(
        title=u'Title',
        default=u'Workspace',
    )


class IWorkspace(zope.interface.Interface):
    """\
    Model workspace.
    """

    # id would be the actual path on filesystem

    title = zope.schema.TextLine(
        title=u'Title',
        required=False,
    )

    description = zope.schema.Text(
        title=u'Description',
        required=False,
    )

    storage = zope.schema.Choice(
        title=u'Storage Method',
        description=u'The type of storage backend used for this workspace.',
        vocabulary='pmr2.vocab.storage',
    )


# browser related

class IWorkspaceListing(zope.interface.Interface):
    """\
    Returns a list of workspaces.
    """


class IWorkspaceActionsViewlet(zope.interface.Interface):
    """\
    Interface for the Workspace action menu.
    """


class IWorkspaceFilePageView(zope.interface.Interface):
    """\
    Interface for the Workspace action menu.
    """


class IWorkspaceStorageCreate(zope.interface.Interface):
    """\
    Interface for the use by WorkspaceStorageCreateForm.
    """

    # We customized the id so validator can discrimate this against
    # the generate mixin id field.
    id = ObjectId(
        title=u'Id',
        description=u'The identifier of the object, used for URI.',
    )


class IWorkspaceBulkAdd(zope.interface.Interface):
    """\
    Interface for the use by WorkspaceAddForm.
    """

    workspace_list = zope.schema.Text(
        title=u'List of Workspaces',
        description=u'List of Mercurial Repositories created by pmr2_mkhg ' \
                     'that are already moved into the workspace directory.',
        required=True,
    )


class IWorkspaceLogProvider(zope.interface.Interface):
    """\
    Interface that will provide a changelog from a workspace.
    """


class IWorkspaceFileListProvider(zope.interface.Interface):
    """\
    Interface that will provide a list of files from a workspace.
    """


# Workspace utilities

class IWorkspaceFileUtility(zope.interface.Interface):
    """\
    Utilities provided to files within workspaces.
    """

    # provides a view
    id = zope.schema.ASCIILine(
        title=u'Id',
    )

    # provides a view
    view = zope.schema.ASCIILine(
        title=u'View',
    )

    title = zope.schema.TextLine(
        title=u'Title',
    )

    description = zope.schema.TextLine(
        title=u'Description',
    )


# Workspace Menu

class IWorkspaceMenuItem(zope.interface.Interface):
    """workspace Menu item marker"""

zope.interface.directlyProvides(IWorkspaceMenuItem, IMenuItemType)


# Menus

class IFileMenu(IBrowserMenu):
    """File View Menu"""


class IFileSubMenuItem(IBrowserSubMenuItem):
    """workspace submenu item"""
