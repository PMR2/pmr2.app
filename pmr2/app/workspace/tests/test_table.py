from unittest import TestCase, TestSuite, makeSuite

from pmr2.app.workspace import table


class TestTableAdapter(TestCase):
    """
    Test the rendering of tables.
    """

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_table_column_base(self):
        context, request, tbl = None, None, None
        column = table.EscapedItemKeyColumn(context, request, tbl)
        column.itemkey = 'id'
        data = {
            'id': 'test',
        }
        self.assertEqual(column.renderCell(data), u'test')

    def test_table_column_int(self):
        context, request, tbl = None, None, None
        column = table.EscapedItemKeyColumn(context, request, tbl)
        column.itemkey = 'id'
        data = {
            'id': 0,
        }
        self.assertEqual(column.renderCell(data), u'0')

    def test_table_column_str_unicode(self):
        context, request, tbl = None, None, None
        column = table.EscapedItemKeyColumn(context, request, tbl)
        column.itemkey = 'id'
        data = {
            'id': '\xc3\xb6',
        }
        self.assertEqual(column.renderCell(data), u'\xf6')

    def test_table_column_str_bad_unicode(self):
        context, request, tbl = None, None, None
        column = table.EscapedItemKeyColumn(context, request, tbl)
        column.itemkey = 'id'
        data = {
            'id': '\xf0\xb6',
        }
        # XXX assuming latin-1
        self.assertEqual(column.renderCell(data), u'\xf0\xb6')

    def test_table_column_unicode(self):
        context, request, tbl = None, None, None
        column = table.EscapedItemKeyColumn(context, request, tbl)
        column.itemkey = 'id'
        data = {
            'id': u'\u3042',
        }
        self.assertEqual(column.renderCell(data), u'\u3042')


def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(TestTableAdapter))
    return suite

