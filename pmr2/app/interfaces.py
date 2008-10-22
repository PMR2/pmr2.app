from zope import schema
from zope import interface
from Products.ATContentTypes.content.folder import ATFolder


class IPMR2(interface.Interface):
    """\
    Repository is the root container for the entire model repository,
    it also contains attributes on where the files are.
    """

    title = schema.TextLine(
        title=u'Title',
    )

    repo_root = schema.TextLine(
        title=u'Repository Path',
        description=u'Physical path to the root of the Mercurial Repositories',
        readonly=True,
    )


class IWorkspaceContainer(interface.Interface):
    """\
    Container for the model workspaces.
    """

    title = schema.TextLine(
        title=u'Title',
    )


class ISandboxContainer(interface.Interface):
    """\
    Container for the sandboxes (working copies).
    """

    title = schema.TextLine(
        title=u'Title',
    )


class IExposureContainer(interface.Interface):
    """\
    Container for all exposure pages.
    """

    title = schema.TextLine(
        title=u'Title',
    )


class IWorkspace(interface.Interface):
    """\
    Model workspace.
    """

    title = schema.TextLine(
        title=u'Title',
    )

    description = schema.TextLine(
        title=u'Description',
    )


class ISandbox(interface.Interface):
    """\
    Container for the sandboxes (working copies).
    """

    title = schema.TextLine(
        title=u'Title',
    )

    description = schema.TextLine(
        title=u'Description',
    )

    status = schema.Text(
        title=u'Status Messages',
        description=u'Output from Mercurial',
    )


class IExposure(interface.Interface):
    """\
    Container for all exposure pages.
    """

    title = schema.TextLine(
        title=u'Title',
    )

    description = schema.TextLine(
        title=u'Description',
    )

    # FIXME placeholder - curation will have its own type.
    curation = schema.TextLine(
        title=u'Curation',
    )

