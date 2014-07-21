import os.path
import zope.interface
import zope.component

from pmr2.app.settings.interfaces import IPMR2GlobalSettings

from pmr2.app.interfaces.exceptions import *

from pmr2.app.workspace.storage import ProtocolResult

from pmr2.app.workspace.interfaces import IStorageProtocol
from pmr2.app.workspace.interfaces import IStorageUtility
from pmr2.app.workspace.interfaces import IWorkspace
from pmr2.app.workspace.interfaces import IWorkspaceListing
from pmr2.app.workspace.exceptions import *


def WorkspaceStorageAdapter(workspace):
    """\
    Adapts a given `Workspace` into a `Storage`.
    """

    assert IWorkspace.providedBy(workspace)
    storage_util = zope.component.queryUtility(
        IStorageUtility, name=workspace.storage)
    if storage_util is None:
        raise UnknownStorageTypeError('cannot acquire storage backend',
            workspace.storage)
    return storage_util(workspace)


class StorageProtocolAdapter(object):
    """\
    Adapters a storage and request into a helper that will only process
    the protocol request.
    """

    # Should we consider adapting a storage object instead?

    zope.interface.implements(IStorageProtocol)

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.storage_util = zope.component.queryUtility(
            IStorageUtility, name=context.storage)
        self.enabled = self.storage_util.isprotocol(self.request)

    def __call__(self):
        if self.enabled:
            result = self.storage_util.protocol(self.context, self.request)
            if not isinstance(result, ProtocolResult):
                # legacy implementation that only process raw client results
                event = None
                if self.request.method in ['POST']:
                    # Assume all POST requests are pushes.
                    event = 'push'
                result = ProtocolResult(result, event)
            return result

        # This isn't a protocol request according to isprotocol.  While
        # it is still possible to directly call the protocol but that's
        # unchecked.
        raise NotProtocolRequestError()


class WorkspaceListing(object):
    """\
    XXX incompatible with v0.4

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
