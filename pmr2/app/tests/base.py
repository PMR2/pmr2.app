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
