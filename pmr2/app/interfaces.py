import zope.schema
import zope.interface

from zope.i18nmessageid import MessageFactory
_ = MessageFactory("pmr2")

from pmr2.app.schema import ObjectId, WorkspaceList


class ObjectIdExistsError(zope.schema.ValidationError):
    __doc__ = _("""The specified id is already in use.""")


class InvalidPathError(zope.schema.ValidationError):
    __doc__ = _("""The value specified is not a valid path.""")


class RepoRootNotExistsError(zope.schema.ValidationError):
    __doc__ = _("""The repository root at the specified path does not exist.""")


class RepoNotExistsError(zope.schema.ValidationError):
    __doc__ = _("""The repository at the specified path does not exist.""")


class RepoPathUndefinedError(zope.schema.ValidationError):
    __doc__ = _("""The repository path is undefined.""")


class WorkspaceDirNotExistsError(zope.schema.ValidationError):
    __doc__ = _("""The workspace directory does not exist.""")


class IObjectIdMixin(zope.interface.Interface):
    """\
    For use by any interface that will be used by AddForm; this
    basically gives an 'id' field for the user to input.
    """

    id = ObjectId(
        title=u'Id',
        description=u'The identifier of the object, used for URI.',
    )


class IPMR2(zope.interface.Interface):
    """\
    Interface for the root container for the entire model repository.
    """

    title = zope.schema.TextLine(
        title=u'Title',
        description=u'The title or name given to this repository.',
    )

    repo_root = zope.schema.BytesLine(
        title=u'Repository Path',
        description=u'The working directory of this repository. This '
                     'directory contains the raw VCS repositories of the '
                     'models.',
        readonly=False,
    )

    # workspace_path is 'workspace'
    # sandbox_path is 'sandbox'


class IPMR2Add(IObjectIdMixin, IPMR2):
    """\
    Interface for the use by PMR2AddForm.
    """


class IWorkspaceContainer(zope.interface.Interface):
    """\
    Container for the model workspaces.
    """

    title = zope.schema.TextLine(
        title=u'Title',
        default=u'Workspace',
    )

    get_repository_list, = zope.schema.accessors(WorkspaceList(
        title=u'Repository List',
        readonly=True,
    ))

    def get_path():
        """\
        Returns the root directory where all the workspaces are stored.
        """


class ISandboxContainer(zope.interface.Interface):
    """\
    Container for the sandboxes (working copies).
    """

    title = zope.schema.TextLine(
        title=u'Title',
        default=u'Sandbox',
    )

    def get_path():
        """\
        Returns the root directory where all the sandboxes are stored.
        """


class IExposureContainer(zope.interface.Interface):
    """\
    Container for all exposure pages.
    """

    title = zope.schema.TextLine(
        title=u'Title',
        default=u'Exposure',
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

    def get_path():
        """\
        Returns path on the filesystem to this instance of workspace.
        """

    def get_storage():
        """\
        Instantiates and returns the storage object of this Workspace.
        """

    def get_log(rev=None, branch=None, shortlog=False, datefmt=None):
        """\
        A helper method to return an iterator to the log.

        This calls get_storage
        """


class IWorkspaceAdd(IObjectIdMixin, IWorkspace):
    """\
    Interface for the use by WorkspaceAddForm.
    """


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


class ISandbox(zope.interface.Interface):
    """\
    Container for the sandboxes (working copies).
    """

    title = zope.schema.TextLine(
        title=u'Title',
    )

    description = zope.schema.Text(
        title=u'Description',
    )

    status = zope.schema.Text(
        title=u'Status Messages',
        description=u'Status output from VCS',
    )

    def get_path():
        """\
        Returns path on the filesystem to this instance of sandbox.
        """


class IExposure(zope.interface.Interface):
    """\
    Container for all exposure pages.
    """

    title = zope.schema.TextLine(
        title=u'Title',
    )

    workspace = zope.schema.TextLine(
        title=u'Workspace',
        description=u'The model workspace this exposure encapsulates.',
    )

    commit_id = zope.schema.TextLine(
        title=u'Commit ID',
        description=u'The specific commit identifier of the model.',
    )

    # FIXME placeholder - curation will have its own type.
    curation = zope.schema.TextLine(
        title=u'Curation',
        required=False,
    )

    def get_path():
        """\
        Returns path on the filesystem to this instance of workspace.
        """

    def get_storage():
        """\
        Instantiates and returns the storage object of this Workspace.
        """

    def get_log(rev=None, branch=None, shortlog=False, datefmt=None):
        """\
        A helper method to return an iterator to the log.
        """


class IExposureDocGen(zope.interface.Interface):
    """\
    Interface for the documentation generation.
    """

    filename = zope.schema.Choice(
        title=u'Documentation File',
        description=u'The file where the documentation resides in.',
        vocabulary='ManifestListVocab',
    )

    transform = zope.schema.Choice(
        title=u'Document Processor',
        description=u'The method to convert the file selected into HTML for use by exposure.',
        vocabulary='PMR2TransformsVocab',
        required=False,
    )


class IExposureDocument(zope.interface.Interface):
    """\
    Interface for an exposure document.
    """

    origin = zope.schema.TextLine(
        title=u'Origin File',
        description=u'Name of the file that this document was generated from.',
        required=False,
    )

    transform = zope.schema.TextLine(
        title=u'Transform',
        description=u'Name of the transform that this was generated from.',
        required=False,
    )

    def generate_content(data):
        """\
        The method to generate/populate content from form input.
        """


class IExposureMathDocument(IExposureDocument):
    """\
    Exposure Document with embedded MathML.
    """

    mathml = zope.schema.Text(
        title=u'MathML',
        description=u'The MathML content',
    )


class IExposureCmetaDocument(IExposureDocument):
    """\
    Exposure Document that handles CellML Metadata.
    """

    metadata = zope.schema.Text(
        title=u'Metadata',
        description=u'The metadata content',
    )

    citation_authors = zope.schema.List(
        title=u'Citation Authors',
        description=u'List of authors of this citation',
    )

    citation_title = zope.schema.TextLine(
        title=u'Citation Title',
        description=u'The title of this citation (e.g. the title of a journal article)',
    )

    citation_bibliographicCitation = zope.schema.TextLine(
        title=u'Bibliographic Citation',
        description=u'The source of the article',
    )

    citation_id = zope.schema.TextLine(
        title=u'Citation Id',
        description=u'The unique identifier for this citation (such as Pubmed).',
    )

    def get_author_family_index():
        """\
        Returns the family name of the list of authors for the index.
        """

