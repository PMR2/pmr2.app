from os import getenv, makedirs
from os.path import join, exists, isdir

from persistent import Persistent
from zope.annotation import factory, IAttributeAnnotatable
from zope.container.contained import Contained
from zope.component.hooks import getSite, getSiteManager
import zope.schema
import zope.interface
import zope.component

from zope.i18nmessageid import MessageFactory
_ = MessageFactory('pmr2')

from AccessControl import Unauthorized
from OFS.interfaces import ITraversable

try:
    from Products.CMFCore.interfaces import ISiteRoot
except ImportError:
    ISiteRoot = None
from Products.CMFCore.utils import getToolByName

from pmr2.app.factory import NamedUtilBase

from pmr2.app.settings.interfaces import IPMR2GlobalSettings
from pmr2.app.settings.interfaces import IPMR2PluggableSettings



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
    default_exposure_idgen = zope.schema.fieldproperty.FieldProperty(
        IPMR2GlobalSettings['default_exposure_idgen'])
    create_user_workspace = zope.schema.fieldproperty.FieldProperty(
        IPMR2GlobalSettings['create_user_workspace'])
    workspace_idgen = zope.schema.fieldproperty.FieldProperty(
        IPMR2GlobalSettings['workspace_idgen'])

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

    def _createContainer(self, container, name, root=None, createDir=False):
        # We need a context that can be traversed using absolute paths,
        # but the site manager acquired ones do not provide this.
        # 
        # So we work around using getSite, but with the caveat that it
        # might not work because of how getSite may acquire the wrong
        # object because this method may be called under a different
        # context, which we will abort.

        if not getSiteManager(self) == getSiteManager():
            raise Exception('Site manager does not match context')

        site = getSite()
        if root:
            folder = site.unrestrictedTraverse(str(root), None)
            if folder is None:
                # XXX exception type
                raise ValueError('Target root not found')
            # XXX check to make sure folder is folderish
        else:
            folder = site

        existed = folder.unrestrictedTraverse(name, None)
        if existed is not None:
            return False

        folder[name] = container(name)
        folder[name].reindexObject()

        if createDir:
            self.createDir(folder[name])

        return True

    def parsePath(self, pathname):
        value = pathname.rsplit('/', 1)
        if not value:
            return None, None
        name = str(value.pop())
        if not value:
            return name, None
        return name, value[0]

    def createDefaultWorkspaceContainer(self):
        # XXX will not create the associated ATFolder objects if path is
        # nested.
        workspace_args = self.parsePath(self.default_workspace_subpath)
        return self.createWorkspaceContainer(*workspace_args)

    def createDefaultExposureContainer(self):
        # XXX will not create the associated ATFolder objects if path is
        # nested.
        exposure_args = self.parsePath(self.default_exposure_subpath)
        return self.createExposureContainer(*exposure_args)

    def createExposureContainer(self, name, root=None):
        # currently import here to avoid circular import due to
        # maintenance of deprecated import location.
        from pmr2.app.exposure.content import ExposureContainer
        return self._createContainer(ExposureContainer, name, root)

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
        from pmr2.app.workspace.content import WorkspaceContainer
        return self._createContainer(WorkspaceContainer, name, root, 
                                    createDir=True)

    def getCurrentUserWorkspaceContainer(self):
        if not self.create_user_workspace:
            # If we are not using this, the rest is meaningless.
            return self.getWorkspaceContainer()

        pm = getToolByName(self.__parent__, 'portal_membership')
        if pm.isAnonymousUser():
            raise Unauthorized()
        user = pm.getAuthenticatedMember()
        return self.getWorkspaceContainer(user.id)

    def getWorkspaceContainer(self, user=None):
        from pmr2.app.workspace.interfaces import IWorkspaceContainer

        if user is None:
            path = self.default_workspace_subpath
        else:
            path = '%s/%s' % (self.user_workspace_subpath, user)
        # have to use getSite for this.
        site = getSite()
        obj = site.unrestrictedTraverse(str(path), None)
        if obj is not None and not IWorkspaceContainer.providedBy(obj):
            if user is None:
                raise TypeError('the content at the workspace container '
                                'location is not a workspace container')
            else:
                raise TypeError('the content returned is not a user workspace '
                                'container')
        return obj

    def getExposureContainer(self):
        return self.siteManagerUnrestrictedTraverse(
            self.default_exposure_subpath)

    def siteManagerUnrestrictedTraverse(self, subpath):
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

