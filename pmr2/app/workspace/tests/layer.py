import tempfile
import shutil

import zope.component
from Products.CMFPlone.utils import _createObjectByType
from Products.CMFPlone.utils import getToolByName

from pmr2.app.settings.interfaces import IPMR2GlobalSettings

from zope.configuration import xmlconfig
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import IntegrationTesting
from plone.testing import z2

from pmr2.app.tests.layer import PMR2_FIXTURE


class WorkspaceBaseLayer(PloneSandboxLayer):

    defaultBases = (PMR2_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        """
        Load the testing zcml.
        """

        import pmr2.app.workspace.tests
        self.loadZCML('test.zcml', package=pmr2.app.workspace.tests)

    def setUpPloneSite(self, portal):
        """
        Sets up the Plone Site for integration tests using Workspaces
        """

        settings = zope.component.getUtility(IPMR2GlobalSettings)

        # user workspace
        _createObjectByType('Folder', portal, id='w')
        settings.user_workspace_subpath = u'w'
        settings.create_user_workspace = True

        from pmr2.app.workspace.content import WorkspaceContainer
        portal['workspace'] = WorkspaceContainer()

WORKSPACE_BASE_FIXTURE = WorkspaceBaseLayer()

WORKSPACE_BASE_INTEGRATION_LAYER = IntegrationTesting(
    bases=(WORKSPACE_BASE_FIXTURE,),
    name="pmr2.app:workspace_base_integration")


class WorkspaceLayer(PloneSandboxLayer):

    defaultBases = (WORKSPACE_BASE_FIXTURE,)

    def setUpPloneSite(self, portal):
        """
        Sets up the Plone Site for integration tests using Workspaces
        """

        from pmr2.app.workspace.content import Workspace

        def mkdummywks(name):
            w = Workspace(name)
            w.storage = 'dummy_storage'
            portal.workspace[name] = w

        mkdummywks('test')
        mkdummywks('cake')
        mkdummywks('external_root')
        mkdummywks('external_test')

WORKSPACE_FIXTURE = WorkspaceLayer()

WORKSPACE_INTEGRATION_LAYER = IntegrationTesting(
    bases=(WORKSPACE_FIXTURE,),
    name="pmr2.app:workspace_integration")
