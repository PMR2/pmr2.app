from unittest import TestCase, TestSuite, makeSuite

from urllib2 import URLError

from pmr2.app.exposure.urlopen import urlopen


class TestUrlopen(TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_000_filefail(self):
        self.assertRaises(URLError, urlopen, 'file:///')

    def test_001_ftpfail(self):
        self.assertRaises(URLError, urlopen, 'ftp://ftp.mozilla.org/README')

    def test_100_http_success(self):
        fp = urlopen('http://example.com/')
        self.assertTrue(hasattr(fp, 'read'))


def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(TestUrlopen))
    return suite

