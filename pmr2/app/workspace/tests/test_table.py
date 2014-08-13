import unittest
from unittest import TestCase, TestSuite, makeSuite

import zope.component

from Products.PloneTestCase import PloneTestCase as ptc
from Products.CMFCore.utils import getToolByName

from pmr2.app.workspace import table

from pmr2.testing.base import TestRequest


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


class ChangesetAuthorEmailColumnTestCase(ptc.PloneTestCase):

    def test_basic(self):
        item = {'author': 'Test User', 'email': 'testuser@example.com'}
        request = TestRequest()
        col = table.ChangesetAuthorEmailColumn(self.portal, request, None)
        self.assertEqual(col.renderCell(item), 'Test User')

    def test_registered(self):
        item = {'author': 'Test User', 'email': 'testuser@example.com'}
        request = TestRequest()
        col = table.ChangesetAuthorEmailColumn(self.portal, request, None)
        pm = getToolByName(self.portal, 'portal_membership')
        pm.getMemberById('test_user_1_').setProperties(
            fullname='Test User',
            email='testuser@example.com',
        )
        self.assertEqual(col.renderCell(item),
            '<a href="http://nohost/plone/author/test_user_1_">'
            'Test User</a>')

    @unittest.skipIf(not table._EMAIL_MANAGER, 'pmr2.users not installed')
    def test_email_man(self):
        item = {'author': 'Test User', 'email': 'testuser@example.com'}
        from pmr2.users.interfaces import IEmailManager
        from pmr2.users.email import EmailManagerFactory
        request = TestRequest()
        col = table.ChangesetAuthorEmailColumn(self.portal, request, None)
        sm = self.portal.getSiteManager()
        sm.registerAdapter(EmailManagerFactory)
        email_manager = zope.component.getAdapter(self.portal, IEmailManager)
        email_manager.set_email('test_user_1_', ['testuser@example.com'])
        self.assertEqual(col.renderCell(item),
            '<a href="http://nohost/plone/author/test_user_1_">'
            'Test User</a>')


def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(TestTableAdapter))
    suite.addTest(makeSuite(ChangesetAuthorEmailColumnTestCase))
    return suite
