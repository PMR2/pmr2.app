import unittest

from pmr2.app.annotation.viewgen import HTMLDocViewGen


class Dummy(object):

    def Title(self):
        return u'Dummy Title'


class ViewGenTestCase(unittest.TestCase):

    def test_html_gen_notitle(self):
        context = Dummy()
        input_ = '<html><head></head></html>'
        generator = HTMLDocViewGen(context, input=input_)
        result = generator.generateTitle()
        self.assertEqual(result, u'Dummy Title')

    def test_html_gen_standard(self):
        context = Dummy()
        input_ = '<html><head><title>Hello World!</title></head></html>'
        generator = HTMLDocViewGen(context, input=input_)
        result = generator.generateTitle()
        self.assertEqual(result, u'Hello World!')

    def test_html_gen_standard_unicode(self):
        context = Dummy()
        # The input is fed in as bytes, however the source could be in
        # unicode encoded in utf8
        input_ = (
            u'<html>'
            u'<head><title>\u3053\u3093\u306b\u3061\u306f\uff01</title>'
            u'</head></html>'.encode('utf8')
        )
        generator = HTMLDocViewGen(context, input=input_)
        result = generator.generateTitle()
        self.assertEqual(result, u'\u3053\u3093\u306b\u3061\u306f\uff01')
