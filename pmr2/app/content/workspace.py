import zope.deprecation

from pmr2.app.workspace.content import Workspace
from pmr2.app.workspace.content import WorkspaceContainer

zope.deprecation.deprecated('Workspace',
    'Please use the archetype tool in the ZMI to update the schema for '
    'Workspace before pmr2.app-0.5.')

zope.deprecation.deprecated('WorkspaceContainer',
    'Please use the archetype tool in the ZMI to update the schema for '
    'WorkspaceContainer before pmr2.app-0.5.')
