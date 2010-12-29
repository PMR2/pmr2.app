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
from pmr2.app.workspace.tests.base import WorkspaceDocTestCase


@onsetup
def setup():
    import pmr2.app
    fiveconfigure.debug_mode = True
    zcml.load_config('configure.zcml', pmr2.app)
    fiveconfigure.debug_mode = False
    ztc.installPackage('pmr2.app')

@onteardown
def teardown():
    pass

setup()
teardown()
ptc.setupPloneSite(products=('pmr2.app',))


class ExposureDocTestCase(WorkspaceDocTestCase):

    def setUp(self):
        """\
        Sets up the environment that the exposure doctest needs.
        """

        WorkspaceDocTestCase.setUp(self)

        self.pmr2.default_exposure_idgen = 'rand128hex'
        self.pmr2.repo_root = self.tmpdir

        from pmr2.app.workspace.content import WorkspaceContainer, Workspace
        from pmr2.app.tests import utils
        self.portal['workspace'] = WorkspaceContainer()
        self.portal.workspace['eggs'] = Workspace('eggs')
        utils.mkreporoot(self.pmr2.createDir(self.portal))
        utils.mkrepo(self.pmr2.dirOf(self.portal.workspace.eggs))

        self.portal.workspace['cake'] = Workspace('cake')

        # create real Hg repos

        import pmr2.mercurial.tests
        from pmr2.mercurial.tests import util
        # pmr2.mercurial
        wdir = self.pmr2.createDir(self.portal.workspace)
        util.extract_archive(wdir)
        # pmr2.app
        # XXX Mercurial specific
        p2a_test = join(dirname(pmr2.testing.__file__), 'pmr2.app.testdata.tgz')
        util.extract_archive(wdir, p2a_test)

        self.archive_revs = util.ARCHIVE_REVS
        self.portal.workspace['import1'] = Workspace('import1')
        self.portal.workspace['import2'] = Workspace('import2')
        self.portal.workspace['pmr2hgtest'] = Workspace('pmr2hgtest')
        self.portal.workspace['rdfmodel'] = Workspace('rdfmodel')
