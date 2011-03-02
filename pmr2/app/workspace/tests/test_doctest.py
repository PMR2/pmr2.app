import unittest

from zope.testing import doctestunit, doctest
from zope.component import testing
from Testing import ZopeTestCase as ztc

from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import PloneSite
from Products.PloneTestCase.layer import onsetup

from pmr2.testing.base import DocTestCase
import pmr2.app.workspace

from pmr2.app.workspace.tests import base

def test_suite():
    return unittest.TestSuite([

        # Adapters to access data.
        #ztc.ZopeDocFileSuite(
        #    'adapter.txt', package='pmr2.app.workspace',
        #    test_class=DocTestCase,
        #    optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
        #),

        # Layout wrapper
        ztc.ZopeDocFileSuite(
            'browser/layout.txt', package='pmr2.app.workspace',
            test_class=base.WorkspaceDocTestCase,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
        ),

        # Forms and interactions.
        ztc.ZopeDocFileSuite(
            'browser/browser.txt', package='pmr2.app.workspace',
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
        doctestunit.DocTestSuite(
            module='pmr2.app.workspace.subscriber',
            setUp=testing.setUp, tearDown=testing.tearDown
        ),

    ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
