import unittest

from zope.testing import doctestunit
from zope.component import testing
from Testing import ZopeTestCase as ztc

def test_suite():
    return unittest.TestSuite([

        # test the fields.
        doctestunit.DocTestSuite(
            module='pmr2.app.schema.field',
            setUp=testing.setUp, tearDown=testing.tearDown
        ),

        # test the converters.
        doctestunit.DocTestSuite(
            module='pmr2.app.schema.converter',
            setUp=testing.setUp, tearDown=testing.tearDown
        ),

    ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
