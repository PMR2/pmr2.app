from unittest import TestSuite, makeSuite
from pmr2.testing.base import TestCase
from zope.app.component.hooks import getSite
from Products.CMFCore.utils import getToolByName
from Products.PluggableAuthService.interfaces.plugins import IChallengePlugin

from pmr2.app.tests import base

class TestProductInstall(TestCase):

    def afterSetUp(self):
        self.types = {
            'WorkspaceContainer': None,
            'SandboxContainer': None,
            'ExposureContainer': None,
            'Workspace': None,
            'Sandbox': None,
            'Exposure': 'pmr2_exposure_workflow',
        }

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


def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(TestProductInstall))
    return suite
