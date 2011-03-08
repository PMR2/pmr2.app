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

        # Root form usage tests.
        ztc.ZopeDocFileSuite(
            'browser/layout.txt', package='pmr2.app',
            test_class=base.DocTestCase,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
        ),

        # Root form usage tests.
        ztc.ZopeDocFileSuite(
            'browser/page.txt', package='pmr2.app',
            test_class=base.DocTestCase,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
        ),

        ### inline doctests

        # test the fields.
        doctestunit.DocTestSuite(
            module='pmr2.app.schema.field',
            setUp=testing.setUp, tearDown=testing.tearDown
        ),

        # test the converters.
        doctestunit.DocTestSuite(
            module='pmr2.app.converter',
            setUp=testing.setUp, tearDown=testing.tearDown
        ),

    ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
