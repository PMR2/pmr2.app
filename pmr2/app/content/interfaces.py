import zope.schema
import zope.interface

from pmr2.app.schema import ObjectId, WorkspaceList, CurationDict, TextLineList


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


class ISandboxContainer(zope.interface.Interface):
    """\
    Container for the sandboxes (working copies).
    """

    title = zope.schema.TextLine(
        title=u'Title',
        default=u'Sandbox',
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


class IPMR2Search(zope.interface.Interface):
    """\
    Interface for the search objects.
    """

    title = zope.schema.TextLine(
        title=u'Title',
    )

    description = zope.schema.Text(
        title=u'Description',
        required=False,
    )

    catalog_index = zope.schema.Choice(
        title=u'Index',
        description=u'The index to be use by this search object.',
        vocabulary='pmr2.vocab.indexes',
    )
