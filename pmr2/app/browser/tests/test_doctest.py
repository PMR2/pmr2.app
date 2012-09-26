import unittest
import doctest

from Testing import ZopeTestCase as ztc

from pmr2.testing import base

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
