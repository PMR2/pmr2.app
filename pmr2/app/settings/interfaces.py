import zope.interface
import zope.schema

from zope.i18nmessageid import MessageFactory
_ = MessageFactory("pmr2")


class IPMR2GlobalSettings(zope.interface.Interface):
    """\
    Interface to hold global configuration settings.
    """

    repo_root = zope.schema.BytesLine(
        title=_(u'Repository Root'),
        description=_(u'The working root directory for PMR2, where the files '
                       'that make up the workspaces will be stored.'),
    )

    workspace_idgen = zope.schema.Choice(
        title=_(u'Workspace Id Generator'),
        description=_(u'The id generator for workspaces.  If unselected id '
                       'is user selectable'),
        vocabulary='pmr2.idgen.vocab',
        required=False,
    )

    default_workspace_subpath = zope.schema.TextLine(
        title=_(u'Default Workspace Subpath'),
        description=_(u'The location of default workspace container.'),
        default=u'workspace',
        required=True,
    )

    user_workspace_subpath = zope.schema.TextLine(
        title=_(u'User Workspace Subpath'),
        description=_(u'The root folder for the user workspace containers; '
                       'this folder should be created if not already exists.'),
        required=False,
    )

    create_user_workspace = zope.schema.Bool(
        title=_(u'Enable User Workspace Container'),
        description=_(u'Default location for workspaces will be the workspace '
                       'container located within the user workspace subpath. '
                       'That workspace container will be created the next '
                       'time the user logs in if not already exists.'),
        default=False,
    )

    default_exposure_subpath = zope.schema.TextLine(
        title=_(u'Default Exposure Subpath'),
        description=_(u'The location of default exposure container.'),
        default=u'exposure',
        required=True,
    )

    default_exposure_idgen = zope.schema.Choice(
        title=_(u'Default Exposure Id Generator'),
        description=_(u'The default id generator for exposures'),
        vocabulary='pmr2.idgen.vocab',
        required=True,
    )

    def dirOf(obj=None):
        """\
        Returns the filesystem path for this object.
        """

    def dirCreatedFor(obj=None):
        """\
        Checks whether path exists.  Optionally an object can be passed,
        which then the physical path will be computed for the object.

        Returns the filesystem path if found, or None if not found.
        """

    def createDir(obj=None):
        """\
        Creates the dir for the specified object.
        """

    def createDefaultWorkspaceContainer():
        """\
        Creates the default workspace container object at the location
        specified at default_workspace_subpath.  The directory to store
        the workspaces will be created on the filesystem.
        """

    def createDefaultExposureContainer():
        """\
        Creates the default exposure container object at the location
        specified at default_exposure_subpath.
        """

    def createExposureContainer(name, root=None):
        """\
        Creates an exposure container with the name `name` at the 
        location `root`.
        """

    def createUserWorkspaceContainer(user, override=False):
        """\
        Create a user workspace container at the location specified at
        the default_workspace_subpath, if enabled or override is True.

        Will fail silently if the root container does not exist.
        """

    def createWorkspaceContainer(name, root=None):
        """\
        Creates an workspace container with the name `name` at the 
        location `root`.  The corresponding directory used for storage
        of the workspace data will be created on the filesystem.
        """

    def getWorkspaceContainer(user=None):
        """\
        Returns the workspace container specified at
        default_workspace_subpath.  User may be specified and its
        container will be returned instead.
        """

    def getExposureContainer():
        """\
        Returns the default exposure container specified at
        default_exposure_subpath.
        """


class IPMR2PluggableSettings(zope.interface.Interface):
    """\
    Auxilary settings that are defined by plugins to PMR2 that are
    pluggable into the main settings.
    """


class IDashboard(zope.interface.Interface):
    """\
    Dashboard for PMR2.
    """


class IDashboardOption(zope.interface.Interface):
    """\
    An option appended to the Dashboard.
    """
