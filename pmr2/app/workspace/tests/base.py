from os.path import dirname
from os.path import join

import zope.component
from zope.component import testing
from Testing import ZopeTestCase as ztc
from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import PloneSite
from Products.PloneTestCase.layer import onsetup
from Products.PloneTestCase.layer import onteardown

import pmr2.testing
from pmr2.testing.base import DocTestCase


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
        from pmr2.app.tests import utils
        from pmr2.app.interfaces import IPMR2GlobalSettings
        setup_defaults()
        self.pmr2 = zope.component.getUtility(IPMR2GlobalSettings)
        # force the repo_root unset
        self.pmr2.repo_root = self.tmpdir

    def createRepo(self):
        # create real Hg repos, to be called only after workspace is
        # created and model root path is assigned
        import pmr2.mercurial.tests
        from pmr2.app.workspace.content import Workspace
        from pmr2.mercurial.tests import util
        p = self.pmr2.createDir(self.portal.workspace)
        util.extract_archive(p)
        # pmr2.app
        # XXX Mercurial specific
        p2a_test = join(dirname(pmr2.testing.__file__), 'pmr2.app.testdata.tgz')
        util.extract_archive(p, p2a_test)
        self.portal.workspace['pmr2hgtest'] = Workspace('pmr2hgtest')
        self.portal.workspace['rdfmodel'] = Workspace('rdfmodel')
        self.pmr2hgtest_revs = util.ARCHIVE_REVS
        self.rdfmodel_revs = [
            'b94d1701154be42acf63ee6b4bd4a99d09ba043c',
            '2647d4389da6345c26d168bbb831f6512322d4f9',
            '006f11cd9211abd2a879df0f6c7f27b9844a8ff2',
        ]

    def tearDown(self):
        DocTestCase.tearDown(self)


