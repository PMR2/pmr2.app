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
        if not (self.create_user_workspace or override):
            return
        try:
            userdir = self.getWorkspaceContainer(user)
            if userdir is not None:
                return
        except TypeError:
            return
        self.createWorkspaceContainer(user, self.user_workspace_subpath)

    def createWorkspaceContainer(self, name, root=None):
        folder = self.siteUnrestrictedTraverse(root)
        if folder is None:
            # some error?  also check that this is a folderish type?
            return

        # import here to avoid circular imports
        from pmr2.app.content import WorkspaceContainer
        folder[name] = WorkspaceContainer(name)

        # WorkspaceContainer created, we need to create the dir on the 
        # filesystem.
        #
        # We need the object that can be traversed using absolute paths,
        # but the site manage acquired ones do not provide this.
        # 
        # So we work around using getSite, but with the caveat that it
        # might not work because of how getSite may acquire the wrong
        # object because this method may be called under a different
        # context, which we will abort.

        if not getSiteManager(self) == getSiteManager():
            # so we give up.
            return

        # Assume site is a Plone site.
        site = getSite()
        newpath = str('%s/%s' % (root, name))
        wc = site.unrestrictedTraverse(newpath, None)
        self.createDir(wc)
        wc.reindexObject()

    def getWorkspaceContainer(self, user=None):
        if user is None:
            path = self.default_workspace_subpath
        else:
            path = '%s/%s' % (self.user_workspace_subpath, user)
        obj = self.siteUnrestrictedTraverse(path)
        if obj is not None and not IWorkspaceContainer.providedBy(obj):
            if user is None:
                raise TypeError('the content at the workspace container '
                                'location is not a workspace container')
            else:
                raise TypeError('the content returned is not a user workspace '
                                'container')
        return obj

    def getExposureContainer(self):
        return self.siteUnrestrictedTraverse(self.default_exposure_subpath)

    def siteUnrestrictedTraverse(self, subpath):
        sm = getSiteManager(self)
        path = '../%s' % subpath
        return sm.unrestrictedTraverse(str(path), None)

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

