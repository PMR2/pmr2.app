from pmr2.app._content.root import PMR2

from pmr2.app._content.workspace import WorkspaceContainer
from pmr2.app._content.workspace import Workspace

from pmr2.app._content.sandbox import SandboxContainer
from pmr2.app._content.sandbox import Sandbox

from pmr2.app._content.exposure import ExposureContainer
from pmr2.app._content.exposure import Exposure
from pmr2.app._content.exposure import ExposureDocument
from pmr2.app._content.exposure import ExposureMathDocument
from pmr2.app._content.exposure import ExposureCmetaDocument
from pmr2.app._content.exposure import ExposureCodeDocument

from pmr2.app._content.support import PMR2Search


def catalog_content(obj, event):
    obj.reindexObject()
