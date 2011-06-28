import zope.interface
import zope.component
from zope.schema import fieldproperty
from Acquisition import aq_inner, aq_parent
from Products.CMFCore.utils import getToolByName
from zope.app.component.hooks import getSite

from pmr2.app.settings.interfaces import IPMR2GlobalSettings

from pmr2.app.workspace.exceptions import PathNotFoundError
from pmr2.app.workspace.interfaces import IStorage

from pmr2.app.interfaces import *
from pmr2.app.exposure.interfaces import *
from pmr2.app.browser.interfaces import IPublishTraverse


def ExposureToWorkspaceAdapter(context):
    """\
    Adapts an exposure object into workspace via the catalog.
    """

    q = {'path': context.workspace,}
    catalog = getToolByName(context, 'portal_catalog')

    result = catalog(**q)
    if result:
        return result[0].getObject()

    # no good, try the bruteforce way.
    return ExposureToWorkspaceTraverse(context)

def ExposureToWorkspaceTraverse(context):
    # okay, I guess the catalog is not going to help, we manually
    # try to find this, based on the current assumption
    settings = zope.component.getUtility(IPMR2GlobalSettings)
    root_fragment = context.getPhysicalPath()[0:-2]
    if context.workspace.startswith('/'):
        fullpath = context.workspace
    else:
        # still need to split workspace because of user workspaces.
        workspace = tuple(settings.default_workspace_subpath.split('/'))
        subpath = tuple(context.workspace.split('/'))
        frags = root_fragment + workspace + subpath
        fullpath = '/'.join(frags)

    # XXX unicode to string path, might need to escape into hex (%XX)
    # entities later.
    fullpath = fullpath.encode('utf8')
    sm = zope.component.getSiteManager(context)
    result = sm.unrestrictedTraverse(fullpath, None)
    if result is None:
        # XXX might worth it to give one more shot using the redirect
        # tool, because some one might have moved the workspace.
        raise WorkspaceObjNotFoundError()
    return result

def ExposureStorageAdapter(context):
    workspace = ExposureToWorkspaceAdapter(context)
    storage = zope.component.getAdapter(workspace, IStorage)
    storage.checkout(context.commit_id)
    return storage

def exposureSources(context, _with_workspace=True):
    # this could be nested in some folders, so we need to acquire
    # the parents up to the Exposure object.
    obj = aq_inner(context)
    paths = []
    while obj is not None:
        if IExposure.providedBy(obj):
            # The same adapter is used by the catalog, so we have this
            # flag here.  Might want to clean up this part later.
            if not _with_workspace:
                return obj, None, None
            # as paths were appended...
            paths.reverse()
            workspace = zope.component.queryAdapter(obj,
                name='ExposureToWorkspace',
            )
            return obj, workspace, '/'.join(paths)
        paths.append(obj.getId())
        obj = aq_parent(obj)
    paths.reverse()
    # XXX could benefit from a better exception type?
    raise Exception('cannot acquire Exposure object with `%s`' % paths)

def ExposureObjectWorkspaceAdapter(context):
    return exposureSources(context)[1]


class ExposureSourceAdapter(object):
    """\
    See interface.
    """

    zope.interface.implements(IExposureSourceAdapter)

    def __init__(self, context):
        """
        context - any exposure object
        """

        self.context = context

    def source(self, _with_workspace=True):
        return exposureSources(self.context, _with_workspace)

    def exposure(self):
        return self.source(False)[0]

    def file(self):
        """\
        Returns contents of this file.
        """

        # While a view could technically be defined to return this, it 
        # is better to generate the redirect to the actual file in the
        # workspace.

        # caching this potentially expensive OP?

        exposure, workspace, path = self.source()
        storage = zope.component.queryAdapter(workspace, IStorage)
        storage.checkout(exposure.commit_id)
        return storage.file(path)
