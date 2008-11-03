import zope.schema
import zope.interface

from zope.i18nmessageid import MessageFactory
_ = MessageFactory("pmr2")

from pmr2.app.schema import ObjectId


class ObjectIdExistsError(zope.schema.ValidationError):
    __doc__ = _("""The specified id is already in use.""")


class InvalidPathError(zope.schema.ValidationError):
    __doc__ = _("""The value specified is not a valid path.""")


class RepoRootNotExistsError(zope.schema.ValidationError):
    __doc__ = _("""The repository root at the specified path does not exist.""")


class RepoNotExistsError(zope.schema.ValidationError):
    __doc__ = _("""The repository at the specified path does not exist.""")


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
                     'directory contains the Mercurial repositories of the '
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


class ISandboxContainer(zope.interface.Interface):
    """\
    Container for the sandboxes (working copies).
    """

    title = zope.schema.TextLine(
        title=u'Title',
        default=u'Sandbox',
    )


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
        readonly=True,
    )

    description = zope.schema.TextLine(
        title=u'Description',
    )


class ISandbox(zope.interface.Interface):
    """\
    Container for the sandboxes (working copies).
    """

    title = zope.schema.TextLine(
        title=u'Title',
    )

    description = zope.schema.TextLine(
        title=u'Description',
    )

    status = zope.schema.Text(
        title=u'Status Messages',
        description=u'Output from Mercurial',
    )


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
    )

