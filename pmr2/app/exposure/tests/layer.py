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

import pmr2.testing
from pmr2.testing import utils


class ExposureLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        import pmr2.app
        import pmr2.app.annotation.tests
        import pmr2.app.workspace.tests
        import pmr2.app.exposure.tests

        self.loadZCML(package=pmr2.app)
        self.loadZCML('test.zcml', package=pmr2.app.annotation.tests)
        self.loadZCML('test.zcml', package=pmr2.app.workspace.tests)
        self.loadZCML('test.zcml', package=pmr2.app.exposure.tests)

        z2.installProduct(app, 'pmr2.app')

        self.tmpdir = tempfile.mkdtemp()

    def setUpPloneSite(self, portal):
        """
        Sets up the Plone Site for integration tests using Exposures.
        """

        # install pmr2.app
        self.applyProfile(portal, 'pmr2.app:default')

        # point the physical root for repo_root to the tmpdir.
        self.pmr2 = zope.component.getUtility(IPMR2GlobalSettings)
        self.pmr2.repo_root = self.tmpdir

        # user workspace
        _createObjectByType('Folder', portal, id='w')
        self.pmr2.user_workspace_subpath = u'w'
        self.pmr2.create_user_workspace = True

        self.pmr2.default_exposure_idgen = 'rand128hex'
        self.pmr2.repo_root = self.tmpdir

        from pmr2.app.workspace.content import WorkspaceContainer, Workspace

        portal['workspace'] = WorkspaceContainer()
        def mkdummywks(name):
            w = Workspace(name)
            w.storage = 'dummy_storage'
            portal.workspace[name] = w

        mkdummywks('test')
        mkdummywks('cake')

        # unassigned
        portal.workspace['blank'] = Workspace('blank')

        # legacy test case.
        portal.workspace['eggs'] = Workspace('eggs')
        utils.mkreporoot(self.pmr2.createDir(portal))
        utils.mkrepo(self.pmr2.dirOf(portal.workspace.eggs))

        from pmr2.app.exposure.content import ExposureContainer
        from pmr2.app.exposure.content import ExposureFileType

        portal['exposure'] = ExposureContainer('exposure')

        # Exposure file types
        portal['test_type'] = ExposureFileType('test_type')
        portal.test_type.title = u'Test Type'
        portal.test_type.views = [
            u'edited_note', u'post_edited_note', u'rot13']
        portal.test_type.tags = [u'please_ignore']

        # Filename related testing.
        portal['docgen_type'] = ExposureFileType('docgen_type')
        portal.docgen_type.title = u'Docgen Type'
        portal.docgen_type.views = [u'docgen', u'filename_note']
        portal.docgen_type.tags = []

        # # publish the things
        # pw = getToolByName(portal, "portal_workflow")
        # pw.doActionFor(portal.test_type, "publish")
        # pw.doActionFor(portal.docgen_type, "publish")

        self._mkexposure(portal['exposure'],
            u'/plone/workspace/test', u'2', '1')
        self._mkexposure(portal['exposure'],
            u'/plone/workspace/eggs', u'1', '2')

    def _mkexposure(self, exposure_root, workspace, commit_id, id_):
        from pmr2.app.workspace.content import Workspace
        from pmr2.app.exposure.content import ExposureContainer, Exposure
        from pmr2.idgen.interfaces import IIdGenerator

        settings = zope.component.queryUtility(IPMR2GlobalSettings)
        idgen = zope.component.queryUtility(IIdGenerator,
            name=settings.default_exposure_idgen)
        if not id_:
            id_ = idgen.next()
        else:
            # call it anyway.
            idgen.next()
        e = Exposure(id_)
        e.workspace = workspace
        e.commit_id = commit_id
        exposure_root[id_] = e
        exposure_root[id_].reindexObject()

    def tearDownZope(self, app):
        z2.uninstallProduct(app, 'pmr2.app')
        shutil.rmtree(self.tmpdir, ignore_errors=True)


EXPOSURE_FIXTURE = ExposureLayer()

EXPOSURE_INTEGRATION_LAYER = IntegrationTesting(
    bases=(EXPOSURE_FIXTURE,), name="pmr2.app:exposure_all_integration")
