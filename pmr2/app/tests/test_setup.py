from unittest import TestSuite, makeSuite

from zope.component.hooks import getSite
from zope.traversing.interfaces import BeforeTraverseEvent

from plone.browserlayer.layer import mark_layer

from Products.PloneTestCase import ptc
from Products.CMFCore.utils import getToolByName
from Products.PluggableAuthService.interfaces.plugins import IChallengePlugin

ptc.setupPloneSite(extension_profiles=('pmr2.app:default',))


class TestProductInstall(ptc.PloneTestCase):
    # Using the vanilla ptc test class for we are testing integration
    # of our installation with core Plone parts.

    def afterSetUp(self):
        self.types = {
            'WorkspaceContainer': None,
            'SandboxContainer': None,
            'ExposureContainer': None,
            'Workspace': None,
            'Sandbox': None,
            'Exposure': 'pmr2_exposure_workflow',
        }

        self.addProfile('pmr2.app:default')
        event = BeforeTraverseEvent(self.portal, self.portal.REQUEST)
        mark_layer(self.portal, event)

    def testTypesInstalled(self):
        for t in self.types.keys():
            self.failUnless(t in self.portal.portal_types.objectIds(),
                            '`%s` content type not installed' % t)

    def testWorkflowsInstalled(self):
        for k, wf in self.types.iteritems():
            if wf:
                self.failUnless(wf in self.portal.portal_workflow.objectIds(),
                                'workflow `%s` not installed for `%s`' % 
                                    (wf, k))

    def testChallengeInstalled(self):
        site = getSite()
        uf = getToolByName(site, 'acl_users')
        activated_pn = uf.plugins.listPluginIds(IChallengePlugin)
        self.assertEqual(activated_pn[0], 'pmr2authpas')

    def testLayerApplied(self):
        from pmr2.app.exposure.interfaces import IPMR2ExposureLayer
        from pmr2.app.interfaces import IPMR2AppLayer
        self.assertTrue(IPMR2ExposureLayer.providedBy(self.portal.REQUEST))
        self.assertTrue(IPMR2AppLayer.providedBy(self.portal.REQUEST))


def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(TestProductInstall))
    return suite
