from os.path import join
import unittest
import doctest

from Testing import ZopeTestCase as ztc

from pmr2.testing.base import DocTestCase

from pmr2.app.exposure.tests.base import ExposureDocTestCase
from pmr2.app.exposure.tests.base import CompleteDocTestCase

# XXX should NOT reverse depend on child dependencies.
from pmr2.mercurial.tests.base import MercurialDocTestCase


def test_suite():
    return unittest.TestSuite([

        ## Adapters to access data.
        #ztc.ZopeDocFileSuite(
        #    'adapter.txt', package='pmr2.app.exposure',
        #    test_class=DocTestCase,
        #    optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
        #),

        # Forms and interactions.
        ztc.ZopeDocFileSuite(
            join('browser', 'browser.txt'), package='pmr2.app.exposure',
            # XXX remove this eventually.
            test_class=MercurialDocTestCase,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
        ),

        # Table
        ztc.ZopeDocFileSuite(
            'table.txt', package='pmr2.app.exposure',
            test_class=CompleteDocTestCase,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
        ),

        # Exposure creation wizard
        ztc.ZopeDocFileSuite(
            join('browser', 'wizard.txt'), package='pmr2.app.exposure',
            test_class=CompleteDocTestCase,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
        ),

        # Catalog
        ztc.ZopeDocFileSuite(
            'catalog.txt', package='pmr2.app.exposure',
            test_class=ExposureDocTestCase,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
        ),

        ## Tables.
        #ztc.ZopeDocFileSuite(
        #    'table.txt', package='pmr2.app.exposure',
        #    test_class=DocTestCase,
        #    optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
        #),

    ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
