from os import getenv, makedirs
from os.path import join, exists, isdir

from persistent import Persistent
from zope.annotation import factory, IAttributeAnnotatable
from zope.app.container.contained import Contained
from zope.app.component.hooks import getSite, getSiteManager
import zope.schema
import zope.interface
import zope.component

from zope.i18nmessageid import MessageFactory
_ = MessageFactory('pmr2')

from OFS.interfaces import ITraversable

try:
    from Products.CMFCore.interfaces import ISiteRoot
except ImportError:
    ISiteRoot = None

from pmr2.app.content.interfaces import IWorkspaceContainer
from pmr2.app.interfaces import IPMR2GlobalSettings, IPMR2PluggableSettings
from pmr2.app.factory import NamedUtilBase

__all__ = [
    'PMR2GlobalSettings',
]


class PMR2GlobalSettingsAnnotation(Persistent, Contained):
    """\
    Please refer to IPMR2GlobalSettings
    """

    zope.interface.implements(IPMR2GlobalSettings, IAttributeAnnotatable)
    zope.component.adapts(IAttributeAnnotatable)

    repo_root = zope.schema.fieldproperty.FieldProperty(
        IPMR2GlobalSettings['repo_root'])
    default_workspace_subpath = zope.schema.fieldproperty.FieldProperty(
        IPMR2GlobalSettings['default_workspace_subpath'])
    user_workspace_subpath = zope.schema.fieldproperty.FieldProperty(
        IPMR2GlobalSettings['user_workspace_subpath'])
    default_exposure_subpath = zope.schema.fieldproperty.FieldProperty(
        IPMR2GlobalSettings['default_exposure_subpath'])
    create_user_workspace = zope.schema.fieldproperty.FieldProperty(
        IPMR2GlobalSettings['create_user_workspace'])

    def __init__(self):
        self.repo_root = _make_default_path()

    def dirOf(self, obj=None):
        path = (self.repo_root,)
        if obj is not None:
            if not ITraversable.providedBy(obj):
                raise TypeError('input is not traversable')
            # XXX this does not take into account partial trees!
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

    def createUserWorkspaceContainer(self, user, override=False):
        # import here to avoid circular imports
        from pmr2.app.content import WorkspaceContainer

        if not (self.create_user_workspace or override):
            return
        try:
            userdir = self.getWorkspaceContainer(user)
            if userdir is not None:
                return
        except TypeError:
            return
        sm = getSiteManager(self)
        root = str('../%s' % self.user_workspace_subpath)
        folder = sm.unrestrictedTraverse(root, None)
        if folder is None:
            # some error?  also check that this is a folderish type?
            return
        folder[user] = WorkspaceContainer(user)

        # Folder created, we need to create the dir on the filesystem
        # and this is where it gets a bit magical.  Not at the creation,
        # but at the part for the resolution of the object.  Basically
        # we need to make sure that we get the site object that we want
        # to have the properly traversable set of objects to get to our
        # nely created one, and since the site managers acquired somehow
        # don't provide it, we have this monstrosity until I find the
        # documentation on how to properly acquire the local root that
        # supports proper traversal and not rely on getSite which has
        # returned unexpected sites at times, due to other registration
        # or validation that has taken place elsewhere.

        if not sm == getSiteManager():
            # so we give up.
            return

        # Assume site is a Plone site.
        site = getSite()
        userpath = str('%s/%s' % (self.user_workspace_subpath, user))
        userws = site.unrestrictedTraverse(userpath, None)
        self.createDir(userws)
        # XXX also need to auto assign push role
        userws.reindexObject()

    def getWorkspaceContainer(self, user=None):
        if user is None:
            path = '../%s' % self.default_workspace_subpath
        else:
            path = '../%s/%s' % (self.user_workspace_subpath, user)
        sm = getSiteManager(self)
        obj = sm.unrestrictedTraverse(str(path), None)
        if obj is not None and not IWorkspaceContainer.providedBy(obj):
            if user is None:
                raise TypeError('the content at the workspace container '
                                'location is not a workspace container')
            else:
                raise TypeError('the content returned is not a user workspace '
                                'container')
        return obj

    def getExposureContainer(self):
        sm = getSiteManager(self)
        path = '../%s' % self.default_exposure_subpath
        obj = sm.unrestrictedTraverse(str(path), None)
        return obj

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


PREFIX = 'pmr2.app.settings-'
def settings_factory(klass, name, title=None, fields=None):
    key = PREFIX + name
    result = factory(klass, key)
    result.name = result.title = name
    if title is not None:
        result.title = title
    result.fields = fields
    return result

