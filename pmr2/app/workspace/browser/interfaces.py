import zope.interface
import zope.schema

from pmr2.app.schema import ObjectId


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


class IFileRenderer(zope.interface.Interface):
    """\
    This provides file rendering capability.
    """

    mimetypes = zope.schema.Text(
        title=u'Supported Mimetypes',
        description=u'The mimetypes supported by this renderer.'
    )


class IRendererDictionary(zope.interface.Interface):
    """\
    This provides file rendering capability.
    """

    def match(data):
        """
        match the provided data and return a mimetype.
        """
