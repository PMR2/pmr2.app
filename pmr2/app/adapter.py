import zope.interface
import zope.component
from zope.schema import fieldproperty
from Acquisition import aq_inner, aq_parent
from Products.CMFCore.utils import getToolByName
from zope.location import Location, locate
from zope.app.component.hooks import getSite

from pmr2.mercurial.interfaces import IPMR2StorageBase, IPMR2HgWorkspaceAdapter
from pmr2.mercurial.adapter import PMR2StorageAdapter
from pmr2.mercurial.adapter import PMR2StorageFixedRevAdapter
from pmr2.mercurial.adapter import PMR2StorageRequestAdapter
from pmr2.mercurial.exceptions import PathNotFoundError
from pmr2.mercurial import WebStorage
import pmr2.mercurial.utils

from pmr2.app.interfaces import *
from pmr2.app.interfaces import IPMR2GlobalSettings
from pmr2.app.content.interfaces import *
from pmr2.app.browser.interfaces import IPublishTraverse
from pmr2.app.browser.interfaces import IExposureFileSelectView

__all__ = [
    'PMR2StorageRequestViewAdapter',
    'PMR2ExposureStorageAdapter',
    'PMR2StorageURIResolver',
    'PMR2ExposureStorageURIResolver',
    'ExposureToWorkspaceAdapter',
    'ExposureToWorkspaceTraverse',
    'ExposureSourceAdapter',
    'ExposureFileSelectView',
]


class PMR2StorageRequestViewAdapter(PMR2StorageRequestAdapter):
    """\
    This adapter is more suited from within views that implment
    IPublishTraverse within this product.

    If we customized IPublishTraverse and adapt it into the request
    (somehow) we could possibly do away with this adapter.  We could do
    refactoring later if we have a standard implementation of 
    IPublishTraverse that captures the request path.
    """

    def __init__(self, context, request, view):
        """
        context -
            The object to turn into a workspace
        request -
            The request
        view -
            The view that implements IPublishTraverse
        """

        assert IPublishTraverse.providedBy(view)
        # populate the request with values derived from view.
        if view.traverse_subpath:
            request['rev'] = view.traverse_subpath[0]
            request['request_subpath'] = view.traverse_subpath[1:]
        PMR2StorageRequestAdapter.__init__(self, context, request)


class PMR2ExposureStorageAdapter(PMR2StorageFixedRevAdapter):

    def __init__(self, context):

        self.exposure = context
        self.workspace = zope.component.queryMultiAdapter(
            (context,),
            name='ExposureToWorkspace',
        )
        self._rev = context.commit_id
        self._path = ()
        PMR2StorageFixedRevAdapter.__init__(self, self.workspace, self._rev)
        self.context = context


class PMR2StorageURIResolver(PMR2StorageAdapter):
    """\
    Storage class that supports resolution of URIs.
    """

    @property
    def base_frag(self):
        """
        The base fragment would be the workspace's absolute url.
        """

        return self.context.absolute_url(),

    def path_to_uri(self, rev=None, filepath=None, view=None, validate=True):
        """
        Returns URI to a location within the workspace this exposure is
        derived from.

        Parameters:

        rev
            revision, commit id.  If None, and filepath is requested,
            it will default to the latest commit id.

        filepath
            The path fragment to the desired file.  Examples:

            - 'dir/file' - Link to the file
                e.g. http://.../workspace/name/@@view/rev/dir/file
            - '' - Link to the root of the manifest
                e.g. http://.../workspace/name/@@view/rev/
            - None - The workspace "homepage"

            Default: None

        view
            The view to use.  @@file for the file listing, @@rawfile for
            the raw file (download link).  See browser/configure.zcml 
            for a listing of views registered for this object.

            Default: None (@@rawfile)

        validate
            Whether to validate whether filepath exists.

            Default: True
        """

        if filepath is not None:
            # we only need to resolve the rest of the path here.
            if not view:
                # XXX magic?
                view = '@@rawfile'

            if not rev:
                self._changectx()
                rev = self.rev 

            if validate:
                try:
                    test = self.fileinfo(rev, filepath).next()
                except PathNotFoundError:
                    return None

            frag = self.base_frag + (view, rev, filepath,)
        else:
            frag = self.base_frag

        result = '/'.join(frag)
        return result


class PMR2ExposureStorageURIResolver(
        PMR2ExposureStorageAdapter, PMR2StorageURIResolver):

    def __init__(self, *a, **kw):
        PMR2ExposureStorageAdapter.__init__(self, *a, **kw)

    @property
    def base_frag(self):
        """
        The base fragment would be the workspace's absolute url.
        """

        return self.workspace.absolute_url(),

    def path_to_uri(self, filepath=None, view=None, validate=True):
        """
        Same as above class
        """

        # XXX find ways to remove premature optmization and unify this
        # and the above.

        rev = self.context.commit_id
        if filepath is not None:
            # we only need to resolve the rest of the path here.
            if not view:
                # XXX magic?
                view = '@@rawfile'

            if not rev:
                self._changectx()
                rev = self.rev 

            if validate:
                try:
                    test = self.fileinfo(filepath).next()
                except PathNotFoundError:
                    # attempt to resolve subrepos
                    result = pmr2.mercurial.utils.match_subrepo(
                        self.ctx.substate, filepath)
                    if not result:
                        return None

            frag = self.base_frag + (view, rev, filepath,)
        else:
            frag = self.base_frag

        result = '/'.join(frag)
        return result


def ExposureToWorkspaceAdapter(context):
    """\
    Adapts an exposure object into workspace via the catalog.
    """

    # There are two methods in place, depending on whether or not 
    # context.workspace starts with '/'.  Formerly the location of
    # workspaces and exposures are assumed, so only the ids were stored
    # and not the full path as it will be.

    root_fragment = context.getPhysicalPath()[0:-2]
    if context.workspace.startswith('/'):
        # absolute path.
        q = {'path': context.workspace,}
    else:
        settings = zope.component.getUtility(IPMR2GlobalSettings)
        workspace = tuple(settings.default_workspace_subpath.split('/'))
        path = '/'.join(root_fragment + workspace)
        q = {
            'id': context.workspace,
            'path': {
                'query': path,
                'depth': len(workspace),
            }
        }

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
        raise WorkspaceObjNotFoundError()
    return result


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
        # this could be nested in some folders, so we need to acquire
        # the parents up to the Exposure object.
        obj = aq_inner(self.context)
        paths = []
        while obj is not None:
            if IExposure.providedBy(obj):
                if not _with_workspace:
                    return obj, None, None
                # as paths were appended...
                paths.reverse()
                workspace = zope.component.queryMultiAdapter(
                    (obj,),
                    name='ExposureToWorkspace',
                )
                return obj, workspace, '/'.join(paths)
            paths.append(obj.getId())
            obj = aq_parent(obj)
        # XXX could benefit from a better exception type?
        raise ValueError('cannot acquire Exposure object')

    def exposure(self):
        return self.source(False)[0]

    def file(self):
        """\
        Returns contents of this file.
        """

        # While a view could technically be defined to return this, it 
        # is better to generate the redirect to the actual file in the
        # workspace.

        exposure, workspace, path = self.source()
        storage = zope.component.queryMultiAdapter(
            (workspace, exposure.commit_id,),
            name='PMR2StorageFixedRev',
        )
        return storage.file(path)


class ExposureFileSelectView(Location):

    zope.interface.implements(IExposureFileSelectView)
    selected_view = fieldproperty.FieldProperty(IExposureFileSelectView['selected_view'])
    views = fieldproperty.FieldProperty(IExposureFileSelectView['views'])

    def __init__(self, context):
        # must locate itself into context the very first thing, as the
        # vocabulary uses source adapter registered above.
        locate(self, context, '')
        # have to assign the views
        self.views = context.views
        # before we can try to assign the selected views do to usage of
        # constrained vocabulary.
        try:
            self.selected_view = context.selected_view
        except:
            pass
