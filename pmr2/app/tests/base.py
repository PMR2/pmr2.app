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

from pmr2.app.workspace.tests.base import WorkspaceDocTestCase


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


class ExposureDocTestCase(WorkspaceDocTestCase):

    def setUp(self):
        """\
        Sets up the environment that the exposure doctest needs.
        """

        WorkspaceDocTestCase.setUp(self)
        self.pmr2.repo_root = self.tmpdir
        from pmr2.app.workspace.content import WorkspaceContainer, Workspace
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
