import zope.schema
import zope.interface

from zope.i18nmessageid import MessageFactory
_ = MessageFactory("pmr2")

from pmr2.app.schema import ObjectId
from pmr2.app.interfaces.exceptions import *


# Interfaces

class IExposureContentIndex(zope.interface.Interface):
    """\
    Interface for methods that will return a workable index.  All 
    exposure objects need to implement this to make catalog contain data
    that will make sense for presentation.

    Basically acquisition of parent methods by child will cause the
    child to be indexed, causing pollution of index and complication in 
    querying.

    Ideally this interface should not have to exist, if the catalog/
    indexing tools are more flexible in allowing what kind of data to 
    include for an object.  Implementation of this class is only a 
    demonstration of what I intend to do, which is to have subobjects
    hold into the keys they hold onto, but the URI will be taken to the
    parent object, and subobjects do not have keys to the parent object.

    Yes, this interface and implementation is a giant workaround of the
    flaws in ZCatalog and how Plone use them.  Unfortunately at this
    stage it is faster to workaround their issues than to roll our own
    cataloging solution based on zope.app.catalog (or RDF store, which
    is in the future).
    """

    def get_authors_family_index():
        pass

    def get_citation_title_index():
        pass

    def get_curation_index():
        pass

    def get_keywords_index():
        pass

    def get_exposure_workspace_index():
        pass


class INamedUtilBase(zope.interface.Interface):
    """\
    Marker interface for the utility generator.
    """


class IExposureSourceAdapter(zope.interface.Interface):
    """\
    Provides any Exposure related objects with methods that will return
    its source Exposure (root), the Workspace object, the relative path
    within it and the content of the file.
    """

    def source():
        """\
        returns a tuple containing its root exposure object, workspace 
        object and the full path of the actual file in this order.
        """

    def file():
        """\
        returns the string of the file itself.
        """


class IPMR2GlobalSettings(zope.interface.Interface):
    """\
    Interface to hold global configuration settings.
    """

    repo_root = zope.schema.BytesLine(
        title=_(u'Repository Root'),
        description=_(u'The working root directory for PMR2, where the files '
                       'that make up the workspaces will be stored.'),
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

    default_exposure_subpath = zope.schema.TextLine(
        title=_(u'Default Exposure Subpath'),
        description=_(u'The location of default exposure container.'),
        default=u'exposure',
        required=True,
    )

    create_user_workspace = zope.schema.Bool(
        title=_(u'Create User Workspaces'),
        description=_(u'Create a user workspace folder within the default '
                       'workspace specified above automatically upon user '
                       'logging in, to let them add their own private '
                       'workspaces.'),
        default=False,
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


class IPMR2KeywordProvider(zope.interface.Interface):
    """\
    A provider of keywords that are captured from the object.

    Even though currently notes are the primary provider of data, which
    by extension provides the keywords for a particular file, the 
    indexed terms will be anchored on the parent object rather than the
    note.  If a note wish to manually be referenced it must generate the
    right values which can uniquely identify the note, and the view must
    be overridden to link to the intended results.
    """
