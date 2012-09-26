from os.path import join
import unittest
import doctest

from zope.component import testing
from Testing import ZopeTestCase as ztc

from pmr2.testing.base import DocTestCase
from pmr2.app.workspace.tests import base

def test_suite():
    return unittest.TestSuite([

        # Adapters to access data.
        #ztc.ZopeDocFileSuite(
        #    'adapter.txt', package='pmr2.app.workspace',
        #    test_class=DocTestCase,
        #    optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
        #),

        # Forms and interactions.
        ztc.ZopeDocFileSuite(
            join('browser', 'browser.txt'), package='pmr2.app.workspace',
            test_class=base.WorkspaceDocTestCase,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
        ),

        # widget converter
        ztc.ZopeDocFileSuite(
            join('widgets', 'converter.txt'), package='pmr2.app.workspace',
            test_class=base.WorkspaceDocTestCase,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
        ),

        # the custom select widget.
        ztc.ZopeDocFileSuite(
            join('widgets', 'select.txt'), package='pmr2.app.workspace',
            test_class=base.WorkspaceDocTestCase,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
        ),

        # Tables.
        ztc.ZopeDocFileSuite(
            'table.txt', package='pmr2.app.workspace',
            test_class=DocTestCase,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
        ),

        # Subscriber
        doctest.DocTestSuite(
            module='pmr2.app.workspace.subscriber',
            setUp=testing.setUp, tearDown=testing.tearDown
        ),

    ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
