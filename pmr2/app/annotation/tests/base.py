from os.path import dirname, join

from Testing import ZopeTestCase as ztc

from Zope2.App import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup, onteardown


@onsetup
def setup():
    import pmr2.app.annotation
    fiveconfigure.debug_mode = True
    zcml.load_config('configure.zcml', pmr2.app.annotation)
    zcml.load_config(join('tests', 'test.zcml'), pmr2.app.annotation)
    fiveconfigure.debug_mode = False
    ztc.installPackage('pmr2.app')

@onteardown
def teardown():
    pass

setup()
teardown()
ptc.setupPloneSite(products=('pmr2.app',))
