import zope.interface
import zope.schema

from pmr2.app.schema import ObjectId


class IStorage(zope.interface.Interface):
    """
    Storage interface.
    """


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

#    backend = zope.schema.Choice(
#        title=u'Backend',
#        description=u'The repository format.',
#        vocabulary='pmr2.vocab.backend',
#    )


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
