import zope.interface
import zope.component

import pmr2.mercurial.interfaces
import pmr2.mercurial.utils

from pmr2.app.interfaces.exceptions import *
from pmr2.app.interfaces import IPMR2GlobalSettings

from pmr2.app.content.interfaces import IWorkspace

from pmr2.app.workspace.interfaces import IWorkspaceListing


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

