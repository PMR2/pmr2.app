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

import pmr2.app.annotation
from pmr2.testing.base import TestRequest


@onsetup
def setup():
    import pmr2.app
    fiveconfigure.debug_mode = True
    zcml.load_config('configure.zcml', pmr2.app.annotation)
    zcml.load_config('tests/test.zcml', pmr2.app.annotation)
    fiveconfigure.debug_mode = False
    ztc.installPackage('pmr2.app')

@onteardown
def teardown():
    pass

setup()
teardown()
ptc.setupPloneSite(products=('pmr2.app',))
