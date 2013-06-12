from unittest import TestCase, TestSuite, makeSuite

from pmr2.app.workspace.browser.util import *


class HtmlFormatTestCase(TestCase):

    def test_img(self):
        raw = (
            '<html><body>'
            '<h1>Info</h1>'
            '<img src="logo.png" height=40>'
            '<img src="/logo.png" height=40 />'
            '<img src="http://example.com/logo.png" height=40 />'
            '</body></html>'
        )

        result = fix_workspace_html_anchors(raw,
            'http://models.example.com/w/test', 'abcdef')

        answer = (
            '<html><body>'
            '<h1>Info</h1>'
            '<img src="http://models.example.com/w/test/rawfile/abcdef/'
                'logo.png" height="40">'
            '<img src="/logo.png" height="40">'
            '<img src="http://example.com/logo.png" height="40">'
            '</body></html>'
        )

        self.assertEqual(result, answer)

    def test_anchor(self):
        raw = (
            '<html><body>'
            '<h1>Info</h1>'
            '<a href="http://example.com/">example</a>'
            '<a href="local/file">subpath</a>'
            '<a href="/local/file">root</a>'
            '<a href="#anchor">local anchor</a>'
            '<a href="file.html#anchor">external anchor</a>'
            '</body></html>'
        )

        result = fix_workspace_html_anchors(raw,
            'http://models.example.com/w/test', 'abcdef')

        answer = (
            '<html><body>'
            '<h1>Info</h1>'
            '<a href="http://example.com/">example</a>'
            '<a href="http://models.example.com/w/test/file/abcdef/'
                'local/file">subpath</a>'
            '<a href="/local/file">root</a>'
            '<a href="#anchor">local anchor</a>'
            '<a href="http://models.example.com/w/test/file/abcdef/'
                'file.html#anchor">external anchor</a>'
            '</body></html>'
        )

        self.assertEqual(result, answer)

    def test_img_anchor(self):
        raw = (
            '<html><body>'
            '<h1>Info</h1>'
            '<a href="http://example.com/"><img src="http://logo.example.com">'
                'example</a>'
            '<a href="local/file"><img src="local.png">subpath</a>'
            '</body></html>'
        )

        result = fix_workspace_html_anchors(raw,
            'http://models.example.com/w/test', 'abcdef')

        answer = (
            '<html><body>'
            '<h1>Info</h1>'
            '<a href="http://example.com/"><img src="http://logo.example.com">'
                'example</a>'
            '<a href="http://models.example.com/w/test/file/abcdef/'
                'local/file"><img src="'
                    'http://models.example.com/w/test/rawfile/abcdef/'
                    'local.png">subpath</a>'
            '</body></html>'
        )

        self.assertEqual(result, answer)


def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(HtmlFormatTestCase))
    return suite

