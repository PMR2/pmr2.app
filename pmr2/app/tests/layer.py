import tempfile
import shutil

import zope.component
from pmr2.app.settings.interfaces import IPMR2GlobalSettings

from plone.app.testing import PloneSandboxLayer
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import IntegrationTesting
from plone.testing import z2


class PMR2BaseLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        import pmr2.app
        self.loadZCML(package=pmr2.app)
        z2.installProduct(app, 'pmr2.app')
        self.tmpdir = tempfile.mkdtemp()

    def setUpPloneSite(self, portal):
        """
        Apply the default pmr2.app profile and ensure that the settings
        have the tmpdir applied in.
        """

        # install pmr2.app
        self.applyProfile(portal, 'pmr2.app:default')

        # point the physical root for repo_root to the tmpdir.
        settings = zope.component.getUtility(IPMR2GlobalSettings)
        settings.repo_root = self.tmpdir

    def tearDownZope(self, app):
        z2.uninstallProduct(app, 'pmr2.app')
        shutil.rmtree(self.tmpdir, ignore_errors=True)


PMR2_FIXTURE = PMR2BaseLayer()

PMR2_INTEGRATION_LAYER = IntegrationTesting(
    bases=(PMR2_FIXTURE,), name="pmr2.app:integration")
