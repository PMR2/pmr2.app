import zope.interface

from Products.Archetypes import atapi

from pmr2.app.interfaces import *

from pmr2.app._content.root import PMR2

from pmr2.app._content.workspace import WorkspaceContainer
from pmr2.app._content.workspace import Workspace

from pmr2.app._content.sandbox import SandboxContainer
from pmr2.app._content.sandbox import Sandbox

from pmr2.app._content.exposure import ExposureContainer
from pmr2.app._content.exposure import Exposure
from pmr2.app._content.exposure import ExposureFile
from pmr2.app._content.exposure import ExposureFolder

from pmr2.app._content.support import PMR2Search


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
