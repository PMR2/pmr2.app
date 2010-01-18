import zope.interface

from Products.Archetypes import atapi

from pmr2.app.interfaces import *

from pmr2.app.content.root import PMR2

from pmr2.app.content.workspace import WorkspaceContainer
from pmr2.app.content.workspace import Workspace

from pmr2.app.content.sandbox import SandboxContainer
from pmr2.app.content.sandbox import Sandbox

from pmr2.app.content.exposure import ExposureContainer
from pmr2.app.content.exposure import Exposure
from pmr2.app.content.exposure import ExposureFile
from pmr2.app.content.exposure import ExposureFolder

from pmr2.app.content.support import PMR2Search


# type registration
atapi.registerType(ExposureContainer, 'pmr2.app')
atapi.registerType(Exposure, 'pmr2.app')
atapi.registerType(ExposureFile, 'pmr2.app')
atapi.registerType(ExposureFolder, 'pmr2.app')

def catalog_content(obj, event):
    # for the subscriber event.
    obj.reindexObject()

def recursive_recatalog_content(obj, event):
    # for exposure state changes.
    # we are going to be restrictive in what we do.
    obj.reindexObject()
    if IExposure.providedBy(obj) or IExposureFolder.providedBy(obj):
        for id_, subobj in obj.items():
            recursive_recatalog_content(subobj, event)

__all__ = [
    'PMR2',
    'WorkspaceContainer',
    'Workspace',
    'SandboxContainer',
    'Sandbox',
    'ExposureContainer',
    'Exposure',
    'ExposureFile',
    'ExposureFolder',
    'PMR2Search',
    'catalog_content',
    'recursive_recatalog_content',
]
