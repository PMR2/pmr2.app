from os.path import dirname
from os.path import join

import zope.component
from zope.component import testing
from Testing import ZopeTestCase as ztc
from Zope2.App import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import PloneSite
from Products.PloneTestCase.layer import onsetup
from Products.PloneTestCase.layer import onteardown

from Products.CMFPlone.utils import _createObjectByType

import pmr2.testing
from pmr2.testing import utils
from pmr2.testing.base import DocTestCase
from pmr2.testing.base import TestRequest

from pmr2.app.browser.interfaces import IPublishTraverse

@onsetup
def setup():
    import pmr2.app
    fiveconfigure.debug_mode = True
    # XXX dependant on pmr2.app still
    zcml.load_config('configure.zcml', pmr2.app)
    zcml.load_config('test.zcml', pmr2.app.workspace.tests)
    fiveconfigure.debug_mode = False
    ztc.installPackage('pmr2.app')

@onteardown
def teardown():
    pass

setup()
teardown()
# XXX dependant on pmr2.app still
ptc.setupPloneSite(products=('pmr2.app',))


class WorkspaceDocTestCase(DocTestCase):

    def setUp(self):
        """\
        Sets up the environment that the workspace doctest needs.
        """

        DocTestCase.setUp(self)
        from plone.z3cform.tests import setup_defaults
        from pmr2.app.settings.interfaces import IPMR2GlobalSettings
        setup_defaults()

        # point the physical root for repo_root to the tmpdir.
        self.pmr2 = zope.component.getUtility(IPMR2GlobalSettings)
        self.pmr2.repo_root = self.tmpdir

        # user workspace
        _createObjectByType('Folder', self.portal, id='w')
        self.pmr2.user_workspace_subpath = u'w'
        self.pmr2.create_user_workspace = True

    def traverse(self, context, browserClass, traverse_subpath, request=None):
        """\
        Mimic traverse behavior by a client.
        """

        assert IPublishTraverse.implementedBy(browserClass)
        if request is None:
            request = TestRequest()
        result = browserClass(context, request)
        for i in traverse_subpath:
            result = result.publishTraverse(request, i)
        return result

    def tearDown(self):
        DocTestCase.tearDown(self)


