from os.path import dirname, join
import tempfile
import shutil
import unittest

from zope.testing import doctestunit, doctest
from zope.component import testing
from Testing import ZopeTestCase as ztc

import zope.interface
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
    def __setitem__(self, key, value):
        pass


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

class ExposureDocTestCase(DocTestCase):

    def setUp(self):
        """\
        Sets up the environment that the exposure doctest needs.
        """

        DocTestCase.setUp(self)
        from plone.z3cform.tests import setup_defaults
        from pmr2.app.content import *
        from pmr2.app.tests import utils
        setup_defaults()
        self.folder['repo'] = PMR2('repo')
        self.folder.repo['workspace'] = WorkspaceContainer()
        self.folder.repo.workspace['eggs'] = Workspace('eggs')
        self.folder.repo.repo_root = self.tmpdir
        utils.mkreporoot(self.folder.repo.repo_root)
        utils.mkrepo(self.folder.repo.workspace.get_path(), 'eggs')

        # create real Hg repos

        import pmr2.mercurial.tests
        from pmr2.mercurial.tests import util
        # pmr2.mercurial
        util.extract_archive(self.folder.repo.workspace.get_path())
        # pmr2.app
        p2a_test = join(dirname(__file__), 'pmr2.app.testdata.tgz')
        util.extract_archive(self.folder.repo.workspace.get_path(), p2a_test)

        util.extract_archive(self.folder.repo.workspace.get_path())
        self.archive_revs = util.ARCHIVE_REVS
        self.folder.repo.workspace['import1'] = Workspace('import1')
        self.folder.repo.workspace['import2'] = Workspace('import2')
        self.folder.repo.workspace['pmr2hgtest'] = Workspace('pmr2hgtest')
        self.folder.repo.workspace['rdfmodel'] = Workspace('rdfmodel')

    def tearDown(self):
        DocTestCase.tearDown(self)
