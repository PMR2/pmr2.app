import os.path

from zope import interface
from zope.schema import fieldproperty

from Acquisition import aq_parent, aq_inner

from Products.CMFCore.PortalFolder import PortalFolderBase
from Products.CMFDefault.DublinCore import DefaultDublinCoreImpl

from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin
from Products.ATContentTypes.content.folder import ATFolder, ATBTreeFolder
from Products.Archetypes import atapi

import pmr2.mercurial
import pmr2.mercurial.utils

from pmr2.app.interfaces import *

__all__ = [
    'PMR2',
    'WorkspaceContainer',
    'SandboxContainer',
    'ExposureContainer',
    'Workspace',
    'Sandbox',
    'Exposure',
]


class PMR2(ATFolder):
    """\
    The repository root object.
    """

    interface.implements(IPMR2)

    # title is defined by ATFolder
    repo_root = fieldproperty.FieldProperty(IPMR2['repo_root'])

atapi.registerType(PMR2, 'pmr2.app')


class WorkspaceContainer(ATBTreeFolder):
    """\
    Container for workspaces in PMR2.
    """

    interface.implements(IWorkspaceContainer)

    # title is defined by ATFolder

    def __init__(self, oid='workspace', **kwargs):
        super(WorkspaceContainer, self).__init__(oid, **kwargs)

    def get_path(self):
        """See IWorkspaceContainer"""

        p = aq_parent(aq_inner(self)).repo_root
        if not p:
            return None
        # XXX magic string
        return os.path.join(p, 'workspace')

    def get_repository_list(self):
        """\
        Implementation of the accessor from IWorkspaceContainer
        
        Returns a list of tuples.  Format is:
        - name of directory
        - whether the object associated with is valid.

          - True means yes
          - None means missing
          - False means object should not exist.  It is either the wrong
            type, or the repository directory is missing on the file
            system.
        """

        reporoot = self.get_path()
        if not reporoot:
            raise RepoPathUndefinedError('repo path is undefined')

        try:
            repodirs = pmr2.mercurial.utils.webdir(reporoot)
        except OSError:
            raise WorkspaceDirNotExistsError()

        # code below is slightly naive, performance-wise.  if done in
        # same loop, popping both list as a stack, compare the values
        # that are popped might be faster.

        # objects need to be processed
        # True = correct type (Workspace), False = incorrect type
        items = self.items()
        repoobjs = [
            (i[0], isinstance(i[1], Workspace),)
            for i in items]
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

atapi.registerType(WorkspaceContainer, 'pmr2.app')


class SandboxContainer(ATBTreeFolder):
    """\
    Container for sandboxes in PMR2.
    """

    interface.implements(ISandboxContainer)

    def __init__(self, oid='sandbox', **kwargs):
        super(SandboxContainer, self).__init__(oid, **kwargs)

    def get_path(self):
        """See ISandboxContainer"""

        p = aq_parent(aq_inner(self)).repo_root
        if not p:
            return None
        # XXX magic string
        return os.path.join(p, 'sandbox')

atapi.registerType(SandboxContainer, 'pmr2.app')


class ExposureContainer(ATBTreeFolder):
    """\
    Container for exposures in PMR2.
    """

    interface.implements(IExposureContainer)

    def __init__(self, oid='exposure', **kwargs):
        super(ExposureContainer, self).__init__(oid, **kwargs)

atapi.registerType(ExposureContainer, 'pmr2.app')


class Workspace(BrowserDefaultMixin, atapi.BaseContent):
    """\
    PMR2 Workspace object is used to connect to the repository of model
    and related data.
    """

    interface.implements(IWorkspace)

    description = fieldproperty.FieldProperty(IWorkspace['description'])

    def get_path(self):
        """See IWorkspace"""

        # aq_inner needed to get out of form wrappers
        p = aq_parent(aq_inner(self)).get_path()
        if not p:
            return None
        return os.path.join(p, self.id)

    def get_log(self, rev=None, branch=None, shortlog=False, datefmt=None):
        # XXX quick and dirty method, lacks interface entry
        # XXX valid datefmt values might need to be documented/checked

        storage = self.get_storage()
        return storage.log(rev, branch, shortlog, datefmt).next()

    def get_storage(self):
        # XXX quick and dirty method, lacks interface entry

        path = self.get_path()
        return pmr2.mercurial.Storage(path)

atapi.registerType(Workspace, 'pmr2.app')


class Sandbox(BrowserDefaultMixin, atapi.BaseContent):
    """\
    PMR2 Sandbox object is an editable instance of the workspace.
    """

    interface.implements(ISandbox)

    description = fieldproperty.FieldProperty(ISandbox['description'])
    status = fieldproperty.FieldProperty(ISandbox['status'])

    def get_path(self):
        """See ISandbox"""

        # aq_inner needed to get out of form wrappers
        p = aq_parent(aq_inner(self)).get_path()
        if not p:
            return None
        return os.path.join(p, self.id)

atapi.registerType(Sandbox, 'pmr2.app')


class Exposure(ATFolder):
    """\
    PMR Exposure object is used to encapsulate a single version of any
    given workspace and will allow more clear presentation to users of
    the system.

    This is implemented as a folder to allow inclusion of different 
    types of data that may be generated as part of the exposure process,
    such as data plots for graphs, graphical representation of metadata
    or the generated diagrams of models, or even other types of data.

    Naturally, specific types of extended exposure data will need to
    have classes defined for them.
    """

    interface.implements(IExposure)

    workspace = fieldproperty.FieldProperty(IExposure['workspace'])
    commit_id = fieldproperty.FieldProperty(IExposure['commit_id'])
    curation = fieldproperty.FieldProperty(IExposure['curation'])

atapi.registerType(Exposure, 'pmr2.app')
