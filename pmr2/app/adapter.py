import zope.interface
import zope.component
from zope.publisher.interfaces import IPublishTraverse, IPublisherRequest
from Acquisition import aq_inner, aq_parent
from Products.CMFCore.utils import getToolByName

from pmr2.mercurial.interfaces import IPMR2StorageBase, IPMR2HgWorkspaceAdapter
from pmr2.mercurial.adapter import PMR2StorageAdapter
from pmr2.mercurial.adapter import PMR2StorageRequestAdapter

from pmr2.app.interfaces import *


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

        # populate the request with values derived from view.
        if view.traverse_subpath:
            request['rev'] = view.traverse_subpath[0]
            request['request_subpath'] = view.traverse_subpath[1:]
        PMR2StorageRequestAdapter.__init__(self, context, request)


class PMR2ExposureStorageAdapter(PMR2StorageRequestAdapter):

    def __init__(self, context):

        self.context = context
        self.workspace = zope.component.queryMultiAdapter(
            (context,),
            name='ExposureToWorkspace',
        )
        self._rev = context.commit_id
        self._path = ()
        PMR2StorageAdapter.__init__(self, self.workspace, self._rev)


class PMR2ExposureDocStorageAdapter(PMR2StorageRequestAdapter):

    def __init__(self, context):

        self.context = context
        self.workspace = None
        ctx = aq_inner(context)
        while ctx is not None and self.workspace is None:
            obj = zope.component.queryMultiAdapter(
                (ctx,),
                name='ExposureToWorkspace',
            )
            if obj is not None:
                self.exposure = context
                self.workspace = obj
            ctx = aq_parent(ctx)

        self._rev = self.exposure.commit_id
        self._path = self.context.origin

        PMR2StorageAdapter.__init__(self, self.workspace, self._rev)


class PMR2StorageURIResolver(PMR2StorageAdapter):
    """\
    Storage class that supports resolution of URIs.
    """

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

        frag = self.context.absolute_url(),

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
                except:  # PathNotFound
                    return None

            frag += (view, rev, filepath,)

        result = '/'.join(frag)
        return result


def ExposureToWorkspaceAdapter(context):
    """\
    Adapts an exposure object into workspace.
    """

    # XXX magic string, at least until we support user created workspace
    # root folders.
    workspace_folder = ('workspace',)

    catalog = getToolByName(context, 'portal_catalog')
    path = '/'.join(context.getPhysicalPath()[0:-2] + workspace_folder)

    # XXX path assumption.
    q = {
        'id': context.workspace,
        'path': {
            'query': path,
            'depth': len(workspace_folder),
        }
    }
    result = catalog(**q)
    if not result:
        # XXX manual gathering not implemented.
        raise WorkspaceObjNotFoundError()
    # there should be only one such id in the workspace for this
    # unique result.
    return result[0].getObject()