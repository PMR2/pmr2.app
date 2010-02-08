from os import getenv, makedirs
from os.path import join, exists, isdir

from persistent import Persistent
from zope.annotation import factory, IAttributeAnnotatable
from zope.component import getUtility
import zope.schema
import zope.interface
from zope.app.component.hooks import getSite, getSiteManager

from zope.i18nmessageid import MessageFactory
_ = MessageFactory('pmr2')

from OFS.interfaces import ITraversable

try:
    from Products.CMFCore.interfaces import ISiteRoot
except ImportError:
    ISiteRoot = None

__all__ = [
    'IPMR2GlobalSettings',
    'PMR2GlobalSettings',
]


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

    default_exposure_subpath = zope.schema.TextLine(
        title=_(u'Default Exposure Subpath'),
        description=_(u'The location of default exposure container.'),
        default=u'exposure',
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


class PMR2GlobalSettingsAnnotation(Persistent):
    """\
    Please refer to IPMR2GlobalSettings
    """

    zope.interface.implements(IPMR2GlobalSettings)
    zope.component.adapts(IAttributeAnnotatable)

    repo_root = zope.schema.fieldproperty.FieldProperty(
        IPMR2GlobalSettings['repo_root'])
    default_workspace_subpath = zope.schema.fieldproperty.FieldProperty(
        IPMR2GlobalSettings['default_workspace_subpath'])
    default_exposure_subpath = zope.schema.fieldproperty.FieldProperty(
        IPMR2GlobalSettings['default_exposure_subpath'])

    def __init__(self):
        self.repo_root = _make_default_path()

    def dirOf(self, obj=None):
        path = (self.repo_root,)
        if obj is not None:
            if not ITraversable.providedBy(obj):
                raise TypeError('input is not traversable')
            path = path + obj.getPhysicalPath()[1:]
        return join(*path)

    def dirCreatedFor(self, obj=None):
        path = self.dirOf(obj)
        if isdir(path):
            return path
        return None

    def createDir(self, obj=None):
        path = self.dirOf(obj)
        if isdir(path):
            # If already dir, pretend we made it.
            return path
        if not isdir(path):
            # if some file are in place or file access error, OSError
            # is not trapped
            makedirs(path)
        return path

PMR2GlobalSettings = factory(PMR2GlobalSettingsAnnotation)


def _make_default_path():
    # While ${SOFTWARE_HOME} is typically standard "default" location
    # for application specific files, this product is normally installed 
    # via buildout, hence this directory will be recreated on each 
    # reinstall.  This basically makes it a bad choice for storing any
    # persistent information as they will be unlinked every upgrade.
    # The ${CLIENT_HOME} is more stable, however it might not exist, so
    # we will have fallback.

    suffix = 'pmr2'
    envvar = ['CLIENT_HOME', 'SOFTWARE_HOME']

    for v in envvar:
        root = getenv(v, None)
        if root is not None:
            return join(root, suffix)

    # This should never happen, but None does not make a path.
    return ''
