import os.path
import zope.interface
import zope.component

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
            # XXX placeholder method of getting a listing of directories,
            # currently assuming any directory is valid repo
            paths = os.listdir(reporoot)
            repodirs = [i for i in paths 
                if os.path.isdir(os.path.join(reporoot, i))]
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
