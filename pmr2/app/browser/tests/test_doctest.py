import unittest

from zope.testing import doctestunit, doctest
from zope.component import testing
from Testing import ZopeTestCase as ztc

from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import PloneSite
from Products.PloneTestCase.layer import onsetup

from pmr2.testing import base
import pmr2.app.browser

def test_suite():
    return unittest.TestSuite([

        # Doctest for PMR2 pages
        ztc.ZopeDocFileSuite(
            'page.txt', package='pmr2.app.browser',
            test_class=base.DocTestCase,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
        ),

        # Doctest for PMR2 forms
        ztc.ZopeDocFileSuite(
            'form.txt', package='pmr2.app.browser',
            test_class=base.DocTestCase,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
        ),

    ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
