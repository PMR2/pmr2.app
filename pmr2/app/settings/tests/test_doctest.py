import unittest
import doctest

from Testing import ZopeTestCase as ztc

from pmr2.testing import base


def test_suite():
    return unittest.TestSuite([

        # Content tests.
        ztc.ZopeDocFileSuite(
            'settings.txt', package='pmr2.app.settings',
            test_class=base.DocTestCase,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
        ),

    ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
