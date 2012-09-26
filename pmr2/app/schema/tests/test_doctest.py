import unittest
import doctest

from zope.component import testing

def test_suite():
    return unittest.TestSuite([

        # test the fields.
        doctest.DocTestSuite(
            module='pmr2.app.schema.field',
            setUp=testing.setUp, tearDown=testing.tearDown
        ),

        # test the converters.
        doctest.DocTestSuite(
            module='pmr2.app.schema.converter',
            setUp=testing.setUp, tearDown=testing.tearDown
        ),

    ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
