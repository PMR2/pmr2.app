from Testing import ZopeTestCase as ztc

from Zope2.App import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup, onteardown
from pmr2.testing import base


@onsetup
def setup():
    import pmr2.app
    import pmr2.testing
    fiveconfigure.debug_mode = True
    zcml.load_config('configure.zcml', pmr2.app)
    zcml.load_config('test.zcml', pmr2.testing)
    fiveconfigure.debug_mode = False
    ztc.installPackage('pmr2.app')

@onteardown
def teardown():
    pass

setup()
teardown()
ptc.setupPloneSite(products=('pmr2.app',))


class TestCase(base.TestCase):
    """\
    PMR2 functional test case.
    """
