import zope.interface
import zope.schema
from zope.lifecycleevent.interfaces import IObjectModifiedEvent

from zope.browsermenu.interfaces import IBrowserMenu
from zope.browsermenu.interfaces import IBrowserSubMenuItem
from zope.browsermenu.interfaces import IMenuItemType


class IStorage(zope.interface.Interface):
    """
    Storage class.  Provides the methods to access data behind a 
    workspace.
    """

    # XXX add these properties:

    # read-only properties
    # archive_formats
    #   - archive formats provided by this storage type.
    # rev 
    #   - current revision id
    # shortrev 
    #   - current revision short id

    # read/write properties
    # datefmt - date format

    def archive_info(format):
        """\
        Information on the specified archive `format`.
        """

    def archive(format):
        """\
        Return an archive of `format`.
        """

    def basename(path):
        """\
        Returns the basename of this path, implementation specific to
        the backend in question.
        """

    def checkout(rev=None):
        """\
        Make the revision identified by rev the active revision for
        all file operations.

        rev can be None, it would be the default checkout of the storage
        backend.
        """

    def format(permissions, node, date, size, basename, contents):
        """\
        Takes the parameters and returns a dictionary with a specific
        set of keys as per default implementation.

        permissions 
            - a string representing permissions
        node 
            - the revision identifier, node the file or object resides 
              in.
        date
            - datetime stamp of the file or object
        size
            - the size of the file or object
        path
            - the path of the content
        contents
            - a method or lambda that returns the contents

        The returning value is a dictionary of the above, with a new
        basename key.
        """

    def file(path):
        """\
        Return the contents of the given path.
        """

    def fileinfo(path):
        """\
        Return a structure about the contents of the given path.
        """

    def files():
        """\
        Return the list of files.
        """

    def listdir(path):
        """\
        Returns the list of files within this path.
        """

    def log(start, count, branch=None):
        """\
        Returns a list of log entries, starting from revision, up to
        number count.  Restricting entries to a specific branch is
        specified by optional parameter branch.
        """

    def pathinfo(path):
        """\
        Returns either a list of fileinfo or individual fileinfo.
        """

    def roots(rev=None):
        """
        Return the roots of the revision specified; typically this is a
        list of commits or changesets that have no further parents.
        """

    def clonecmd():
        """
        Return a command to clone the storage.
        """

    def resolve_file(path):
        """
        Like file, but attempts to resolve across subrepos.
        """


class IStorageUtility(zope.interface.Interface):
    """\
    Wrapper around the initialization of its respective storage class.

    This class is used to initialize a storage object from a workspace
    in an implementation agnostic way, as they all have different
    initialization methods (i.e. different on-disk locations, init
    parameters).  This utility separates out the initialization of a
    storage using a Zope/Plone object from specifying raw parameters,
    and also provide a place to put the title and descriptions of
    this particular storage type.
    """

    title = zope.schema.TextLine(
        title=u'Title',
        default=u'Workspace',
    )

    command = zope.schema.TextLine(
        title=u'Command',
        default=u'The name of the binary that is typically associated with '
            'this storage backend.',
    )

    clone_verb = zope.schema.TextLine(
        title=u'Clone Verb',
        default=u'The command "verb" that the default binary use for making '
            'a local checkout on user\'s machine.',
    )

    def create(context):
        """\
        Create or instantiate the backend storage for context.
        """

    def acquireFrom(context):
        """\
        Acquire a Storage Backend from the given context.
        """

    def isprotocol(context, request):
        """\
        Verify that the request is a protocol level request.
        """

    def protocol(context, request):
        """\
        Process the request as a protocol request on context.
        """

    def validateExternalURI(uri):
        """\
        Checks whether uri is a valid external URI.
        """

    def syncWorkspace(context, workspace):
        """\
        Sync context with source workspace object.

        Returns a tuple with result and optional message.
        """

    def syncIdentifier(context, identifier):
        """\
        Sync context with source identified by identifier.

        Returns a tuple with result and optional message.
        """

    def sync(context, source):
        """\
        Generic sync function

        Context will be updated with the data in source, which will
        automatically resolve to the correct method based on the input.

        Returns a tuple with result and optional message.
        """


class IStorageProtocol(zope.interface.Interface):
    """\
    A helper for quick, generic access to adapt a context and request
    into an object specifically for accessing the raw protocol of a
    given storage type.
    """


class IStorageArchiver(zope.interface.Interface):
    """
    A helper named utility for archiving the contents of a storage
    instance.
    """

    label = zope.schema.TextLine(title=u'label')
    suffix = zope.schema.ASCIILine(title=u'Filename Extension')
    mimetype = zope.schema.ASCIILine(title=u'mimetype')

    def enabledFor(storage):
        """
        Checks whether this storage is enabled with this archiver.
        """

    def archive(storage):
        """
        Archives the contents of the storage.
        """


# events

class IWorkspaceModifiedEvent(IObjectModifiedEvent):
    """
    An generic workspace modification event.
    """

    workspace = zope.interface.Attribute('The workspace that was modified.')


class IWorkspaceStorageIncomingEvent(IWorkspaceModifiedEvent):
    """
    An event fired whenever the underlying storage has incoming data,
    i.e. a client push.
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

    storage = zope.schema.Choice(
        title=u'Storage Method',
        description=u'The type of storage backend used for this workspace.',
        vocabulary='pmr2.vocab.storage',
    )


# Workspace utilities

class IWorkspaceListing(zope.interface.Interface):
    """\
    Returns a list of workspaces.
    """


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


class IWorkspaceLogProvider(zope.interface.Interface):
    """\
    Interface that will provide a changelog from a workspace.
    """


class IWorkspaceFileListProvider(zope.interface.Interface):
    """\
    Interface that will provide a list of files from a workspace.
    """


# Workspace viewlets

class IWorkspaceActionsViewlet(zope.interface.Interface):
    """\
    Interface for the Workspace action menu.
    """


# Workspace Menu

class IWorkspaceMenuItem(zope.interface.Interface):
    """workspace Menu item marker"""

zope.interface.directlyProvides(IWorkspaceMenuItem, IMenuItemType)


# Menus

class IFileMenu(IBrowserMenu):
    """File View Menu"""


class IFileSubMenuItem(IBrowserSubMenuItem):
    """workspace submenu item"""


# Misc.

class ICurrentCommitIdProvider(zope.interface.Interface):
    """\
    A utility that will provide the current commit id for this object.
    """

    def current_commit_id(self):
        """\
        Return the current commit id.
        """
