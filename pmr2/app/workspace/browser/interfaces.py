import zope.interface
import zope.schema

from pmr2.app.schema import ObjectId


class IWorkspacePage(zope.interface.Interface):
    """\
    Interface for the main workspace page.
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


class IWorkspaceFork(zope.interface.Interface):
    """\
    Interface for the Fork page.
    """

    id = ObjectId(
        title=u'Id',
        description=u'The identifier for the new workspace.',
    )


class IWorkspaceSync(zope.interface.Interface):
    """\
    Interface for workspace sync form.
    """

    external_uri = zope.schema.ASCIILine(
        title=u'URI',
        description=u'The URI to the data source to sync this workspace with.',
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


class IFileAction(zope.interface.Interface):
    """
    Provides a file action.
    """

    title = zope.schema.Text(
        title=u'Title',
        description=u'The title for this file action',
    )

    description = zope.schema.Text(
        title=u'Description',
        description=u'The description for this file action.',
        required=False,
    )

    def href(view):
        """
        Return the intended href value for this action.
        """


class IDirectoryRenderer(zope.interface.Interface):
    """\
    This is a marker interface for directory listing renderer.
    """


class IRendererDictionary(zope.interface.Interface):
    """\
    This provides file rendering capability.
    """

    def match(data):
        """
        match the provided data and return a mimetype.
        """
