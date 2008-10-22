from zope import interface
from zope.schema import fieldproperty

from Products.CMFCore.PortalFolder import PortalFolderBase
from Products.CMFDefault.DublinCore import DefaultDublinCoreImpl

from pmr2.app.interfaces import *

from Products.ATContentTypes.content.folder import ATFolder, ATBTreeFolder
from Products.Archetypes import atapi

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

atapi.registerType(WorkspaceContainer, 'pmr2.app')


class SandboxContainer(ATBTreeFolder):
    """\
    Container for sandboxes in PMR2.
    """

    interface.implements(ISandboxContainer)

atapi.registerType(SandboxContainer, 'pmr2.app')


class ExposureContainer(ATBTreeFolder):
    """\
    Container for exposures in PMR2.
    """

    interface.implements(IExposureContainer)

atapi.registerType(ExposureContainer, 'pmr2.app')


class Workspace(atapi.BaseContent):
    """\
    PMR2 Workspace object is used to connect to the repository of model
    and related data.
    """

    interface.implements(IWorkspace)

    description = fieldproperty.FieldProperty(IWorkspace['description'])

atapi.registerType(Workspace, 'pmr2.app')


class Sandbox(atapi.BaseContent):
    """\
    PMR2 Sandbox object is an editable instance of the workspace.
    """

    interface.implements(ISandbox)

    description = fieldproperty.FieldProperty(ISandbox['description'])
    status = fieldproperty.FieldProperty(ISandbox['status'])

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
