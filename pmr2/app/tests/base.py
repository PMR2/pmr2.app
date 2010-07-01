from os.path import dirname, join
import tempfile
import shutil
import unittest

from zope.testing import doctestunit, doctest
from zope.component import testing
from Testing import ZopeTestCase as ztc

import zope.interface
import zope.component
from zope.annotation import IAnnotations
import z3c.form.testing

from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import PloneSite
from Products.PloneTestCase.layer import onsetup, onteardown


@onsetup
def setup():
    import pmr2.app
    fiveconfigure.debug_mode = True
    zcml.load_config('configure.zcml', pmr2.app)
    zcml.load_config('tests/test.zcml', pmr2.app)
    fiveconfigure.debug_mode = False
    ztc.installPackage('pmr2.app')

@onteardown
def teardown():
    pass

setup()
teardown()
ptc.setupPloneSite(products=('pmr2.app',))


class TestRequest(z3c.form.testing.TestRequest):
    """\
    Customized TestRequest to mimic missing actions.
    """

    zope.interface.implements(IAnnotations)
    def __init__(self, *a, **kw):
        super(TestRequest, self).__init__(*a, **kw)

    def __setitem__(self, key, value):
        self.form[key] = value

    def __getitem__(self, key):
        try:
            return super(TestRequest, self).__getitem__(key)
        except KeyError:
            return self.form[key]


class TestCase(ptc.PloneTestCase):
    """\
    For standard tests.
    """


class DocTestCase(ptc.FunctionalTestCase):
    """\
    For doctests.
    """

    def setUp(self):
        super(DocTestCase, self).setUp()
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        super(DocTestCase, self).tearDown()
        shutil.rmtree(self.tmpdir, ignore_errors=True)


class WorkspaceDocTestCase(DocTestCase):

    def setUp(self):
        """\
        Sets up the environment that the exposure doctest needs.
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
        from pmr2.app.content import Workspace
        from pmr2.mercurial.tests import util
        p = self.pmr2.createDir(self.portal.workspace)
        util.extract_archive(p)
        # pmr2.app
        p2a_test = join(dirname(__file__), 'pmr2.app.testdata.tgz')
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


class ExposureDocTestCase(WorkspaceDocTestCase):

    def setUp(self):
        """\
        Sets up the environment that the exposure doctest needs.
        """

        WorkspaceDocTestCase.setUp(self)
        self.pmr2.repo_root = self.tmpdir
        from pmr2.app.content import WorkspaceContainer, Workspace
        from pmr2.app.tests import utils
        self.portal['workspace'] = WorkspaceContainer()
        self.portal.workspace['eggs'] = Workspace('eggs')
        utils.mkreporoot(self.pmr2.createDir(self.portal))
        utils.mkrepo(self.pmr2.dirOf(self.portal.workspace.eggs))

        # create real Hg repos

        import pmr2.mercurial.tests
        from pmr2.mercurial.tests import util
        # pmr2.mercurial
        wdir = self.pmr2.createDir(self.portal.workspace)
        util.extract_archive(wdir)
        # pmr2.app
        p2a_test = join(dirname(__file__), 'pmr2.app.testdata.tgz')
        util.extract_archive(wdir, p2a_test)

        self.archive_revs = util.ARCHIVE_REVS
        self.portal.workspace['import1'] = Workspace('import1')
        self.portal.workspace['import2'] = Workspace('import2')
        self.portal.workspace['pmr2hgtest'] = Workspace('pmr2hgtest')
        self.portal.workspace['rdfmodel'] = Workspace('rdfmodel')
