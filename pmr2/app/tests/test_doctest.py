import unittest

from zope.testing import doctestunit, doctest
from zope.component import testing
from Testing import ZopeTestCase as ztc

from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import PloneSite
from Products.PloneTestCase.layer import onsetup

import pmr2.app
import base

def test_suite():
    return unittest.TestSuite([
        # Browser rendering tests, override setup to make rendering
        # more simple.
        ztc.ZopeDocFileSuite(
            'browser.txt', package='pmr2.app',
            test_class=base.DocTestCase,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
        ),

        # Root form usage tests.
        ztc.ZopeDocFileSuite(
            'browser/root.txt', package='pmr2.app',
            test_class=base.DocTestCase,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
        ),

        doctestunit.DocTestSuite(
            module='pmr2.app.schema.field',
            setUp=testing.setUp, tearDown=testing.tearDown
        ),

    ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
