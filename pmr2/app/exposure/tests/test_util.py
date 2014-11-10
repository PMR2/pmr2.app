import unittest

import zope.component
from Products.CMFCore.utils import getToolByName

from pmr2.app.exposure.interfaces import IExposureFile
from pmr2.app.exposure.content import ExposureFile
from pmr2.app.exposure.browser import util

from pmr2.app.annotation import note_factory
from pmr2.app.annotation.tests import adapter
from pmr2.app.annotation.tests import content
from pmr2.app.annotation.interfaces import IExposureFileAnnotator

from pmr2.testing.base import TestRequest
from pmr2.app.exposure.tests import layer


class UtilsTestCase(unittest.TestCase):

    # Just using the integration layer for now until I figure out how to
    # split this off in cleaner ways.
    layer = layer.EXPOSURE_INTEGRATION_LAYER

    def setUp(self):
        self.portal = self.layer['portal']
        ef = ExposureFile('file2')
        self.portal.exposure['2']['file2'] = ef

    def test_mold_views_base(self):
        ctxobj = self.portal.exposure['2'].file2

        request = TestRequest()
        fields = {'views': [('edited_note', {'note': u'value'})]}

        views, hidden_views = util._mold_views(ctxobj, request, fields)
        self.assertEqual(views, ['edited_note'])
        self.assertEqual(hidden_views, [])

    def test_mold_views_hidden(self):
        # register temporary generator and note.

        ctxobj = self.portal.exposure['2'].file2

        sm = zope.component.getSiteManager()
        sm.registerUtility(adapter.EditedNoteAnnotatorFactory, 
            IExposureFileAnnotator, name='edited_note_viewless')
        EditedNoteViewlessFactory = note_factory(
            content.EditedNote, 'edited_note_viewless')
        sm.registerAdapter(EditedNoteViewlessFactory, 
            (IExposureFile,), content.IEditedNote,
            name='edited_note_viewless')

        request = TestRequest()
        fields = {'views': [('edited_note_viewless', {'note': u'value'})]}

        views, hidden_views = util._mold_views(ctxobj, request, fields)
        self.assertEqual(views, ['edited_note_viewless'])
        self.assertEqual(hidden_views, ['edited_note_viewless'])
