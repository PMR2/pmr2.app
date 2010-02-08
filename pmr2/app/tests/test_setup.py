from unittest import TestSuite, makeSuite
from base import TestCase
from Products.CMFCore.utils import getToolByName

class TestProductInstall(TestCase):

    def afterSetUp(self):
        self.types = {
            'PMR2': 'pmr2_root_workflow',
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


def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(TestProductInstall))
    return suite
