import zope.interface
import zope.component

import pmr2.mercurial.interfaces
import pmr2.mercurial.utils
from pmr2.mercurial.adapter import PMR2StorageAdapter
from pmr2.mercurial.adapter import PMR2StorageRequestAdapter

from pmr2.app.interfaces.exceptions import *
from pmr2.app.interfaces import IPMR2GlobalSettings
from pmr2.app.browser.interfaces import IPublishTraverse

from pmr2.app.workspace.interfaces import *


def WorkspaceStorageAdapter(workspace):
    """\
    Adapts a given `Workspace` into a `Storage`.
    """

    assert IWorkspace.providedBy(workspace)
    storage_util = zope.component.queryUtility(
        IStorageUtility, name=workspace.storage)
    if storage_util is None:
        raise ValueError('storage type `%s` unknown' % workspace.storage)
    return storage_util(workspace)


def WorkspaceRequestStorageAdapter(workspace, request):
    """\
    Adapts a given `Workspace` and request into a `Storage`.

    This facilitates "checking out" the correct requested revision.
    """


class WorkspaceListing(object):
    """\
    Returns a list of objects that implements IWorkspace from a given
    context alongside with directories that exist within its associated
    directory located on the file system as defined by the PMR2 
    settings.

    Result format is:
    - name of directory
    - whether the object associated with is valid.

      - True means yes
      - None means missing
      - False means object should not exist.  It is either the wrong
        type, or the repository directory is missing on the file
        system.
    """

    zope.interface.implements(IWorkspaceListing)

    def __init__(self, context):
        self.context = context

    def __call__(self):

        settings = zope.component.getUtility(IPMR2GlobalSettings)
        reporoot = settings.dirCreatedFor(self.context)
        if reporoot is None:
            raise WorkspaceDirNotExistsError()

        try:
            repodirs = pmr2.mercurial.utils.webdir(reporoot)
        except OSError:
            raise WorkspaceDirNotExistsError()

        # code below is slightly naive, performance-wise.  if done in
        # same loop, popping both list as a stack, compare the values
        # that are popped might be faster.

        # objects need to be processed
        # True = correct type (Workspace), False = incorrect type
        items = self.context.items()
        repoobjs = [(i[0], IWorkspace.providedBy(i[1]),) for i in items]
        repoobjs_d = dict(repoobjs)

        # check to see if a repo dir has object of same name
        # None = missing, True/False (from above if exists)
        check = [(i, repoobjs_d.get(i, None)) for i in repodirs]

        # failure due to non-existing objects (remaining repoobjs that
        # were not checked
        # False = repo missing/invalid Workspace object
        fail = [(i[0], False) for i in repoobjs if i[0] not in repodirs]

        # build the result and sort
        result = fail + check
        result.sort()

        return result


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
        Returns URI to a location within the workspace this object is
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


