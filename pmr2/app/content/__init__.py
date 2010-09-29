import zope.interface

from Products.Archetypes import atapi

from pmr2.app.workspace.content import Workspace
from pmr2.app.workspace.content import WorkspaceContainer

zope.deprecation.deprecated('Workspace',
    'Please use the archetype tool in the ZMI to update the schema for '
    'Workspace before pmr2.app-0.5.')

zope.deprecation.deprecated('WorkspaceContainer',
    'Please use the archetype tool in the ZMI to update the schema for '
    'WorkspaceContainer before pmr2.app-0.5.')

from pmr2.app.content.sandbox import SandboxContainer
from pmr2.app.content.sandbox import Sandbox

from pmr2.app.exposure.content import Exposure
from pmr2.app.exposure.content import ExposureContainer
from pmr2.app.exposure.content import ExposureFile
from pmr2.app.exposure.content import ExposureFileType
from pmr2.app.exposure.content import ExposureFolder

zope.deprecation.deprecated('Exposure',
    'Please use the archetype tool in the ZMI to update the schema for '
    'Exposure before pmr2.app-0.5.')

zope.deprecation.deprecated('ExposureContainer',
    'Please use the archetype tool in the ZMI to update the schema for '
    'ExposureContainer before pmr2.app-0.5.')

zope.deprecation.deprecated('ExposureFile',
    'Please use the archetype tool in the ZMI to update the schema for '
    'ExposureFile before pmr2.app-0.5.')

zope.deprecation.deprecated('ExposureFileType',
    'Please use the archetype tool in the ZMI to update the schema for '
    'ExposureFileType before pmr2.app-0.5.')

zope.deprecation.deprecated('ExposureFolder',
    'Please use the archetype tool in the ZMI to update the schema for '
    'ExposureFolder before pmr2.app-0.5.')

from pmr2.app.content.support import PMR2Search


# type registration

__all__ = [
    'WorkspaceContainer',
    'Workspace',
    'SandboxContainer',
    'Sandbox',
    'ExposureContainer',
    'Exposure',
    'ExposureFile',
    'ExposureFileType',
    'ExposureFolder',
    'PMR2Search',
]
