from plone.app.portlets.storage import PortletAssignmentMapping
from plone.portlets.interfaces import IPortletType
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignment
from plone.portlets.interfaces import IPortletDataProvider
from plone.portlets.interfaces import IPortletRenderer
from Products.CMFCore.utils import getToolByName
from zope.component import getUtility, getMultiAdapter, getAdapter

from pmr2.app.exposure.portlets import ExposureFileNotes
from pmr2.app.exposure.portlets import PMR1Curation
from pmr2.app.exposure.portlets import collab
from pmr2.testing.base import TestCase

from .base import CompleteDocTestCase
from pmr2.app.exposure.content import Exposure
from pmr2.app.exposure.content import ExposureFile


# XXX add tests for all other portlets for pmr2.app.exposure.

class TestPortlet(TestCase):

    def afterSetUp(self):
        self.setRoles(('Manager', ))

    def testPortletTypeRegistered(self):
        portlet = getUtility(IPortletType, name='pmr2.portlets.pmr1_curation')
        self.assertEquals(portlet.addview, 'pmr2.portlets.pmr1_curation')

    def testInterfaces(self):
        portlet = PMR1Curation.Assignment(curator_uri='http://example.com')
        self.failUnless(IPortletAssignment.providedBy(portlet))
        self.failUnless(IPortletDataProvider.providedBy(portlet.data))

    def testInvokeAddview(self):
        portlet = getUtility(IPortletType, name='pmr2.portlets.pmr1_curation')
        mapping = self.portal.restrictedTraverse(
            '++contextportlets++plone.leftcolumn')
        for m in mapping.keys():
            del mapping[m]
        addview = mapping.restrictedTraverse('+/' + portlet.addview)
        addview.createAndAdd(data={'curator_uri': 'http://example.com'})
        self.assertEquals(len(mapping), 1)
        self.failUnless(isinstance(mapping.values()[0], 
            PMR1Curation.Assignment))

    def testInvokeEditView(self):
        mapping = PortletAssignmentMapping()
        request = self.folder.REQUEST
        mapping['foo'] = PMR1Curation.Assignment(
            curator_uri='http://example.com')
        editview = getMultiAdapter((mapping['foo'], request), name='edit')
        self.failUnless(isinstance(editview, PMR1Curation.EditForm))

    def testRenderer(self):
        context = self.folder
        request = self.folder.REQUEST
        view = self.folder.restrictedTraverse('@@plone')
        manager = getUtility(IPortletManager, name='plone.rightcolumn', 
            context=self.portal)
        assignment = PMR1Curation.Assignment(curator_uri='http://example.com')

        renderer = getMultiAdapter(
            (context, request, view, manager, assignment), IPortletRenderer)
        self.failUnless(isinstance(renderer, PMR1Curation.Renderer))


class TestRenderer(TestCase):

    def afterSetUp(self):
        self.setRoles(('Manager', ))

    def renderer(self, context=None, request=None, view=None, manager=None, assignment=None):
        context = context or self.folder
        request = request or self.folder.REQUEST
        view = view or self.folder.restrictedTraverse('@@plone')
        manager = manager or getUtility(IPortletManager, name='plone.rightcolumn', context=self.portal)
        assignment = assignment or PMR1Curation.Assignment(curator_uri='http://example.com')

        return getMultiAdapter((context, request, view, manager, assignment), IPortletRenderer)

    def test_render(self):
        r = self.renderer(context=self.portal, assignment=PMR1Curation.Assignment(curator_uri='http://example.com'))
        r = r.__of__(self.folder)
        r.update()
        output = r.render()
        self.assertTrue('http://example.com' in output)
        self.assertTrue('Report curation issue.' in output)

    def test_modded_label_render(self):
        r = self.renderer(context=self.portal, assignment=PMR1Curation.Assignment(curator_uri='http://example.com', contact_label=u'Contact.'))
        r = r.__of__(self.folder)
        r.update()
        output = r.render()
        self.assertTrue('http://example.com' in output)
        self.assertFalse('Report curation issue.' in output)
        self.assertTrue('Contact.' in output)


class TestPMR1CurationValues(TestCase):

    def afterSetUp(self):
        self.setRoles(('Manager', ))
        self.exposure = Exposure('test')

    def renderer(self, context=None, request=None, view=None, manager=None, assignment=None):
        context = context or self.folder
        request = request or self.folder.REQUEST
        view = view or self.folder.restrictedTraverse('@@plone')
        manager = manager or getUtility(IPortletManager, name='plone.rightcolumn', context=self.portal)
        assignment = assignment or PMR1Curation.Assignment(
            curator_uri='http://example.com')
        renderer = getMultiAdapter((context, request, view, manager, assignment), IPortletRenderer)
        # Pretend this is done...
        renderer.exposure = self.exposure
        return renderer

    def testCurationValuesNone(self):
        renderer = self.renderer()
        result = renderer.pmr1_curation()
        self.assertEqual(result, [
            {'label': u'Curation Status:', 'stars': u'0',},
        ])

    def testCurationValuesBase(self):
        self.exposure.curation = {
            u'pmr_curation_star': [u'1'], 
        }

        renderer = self.renderer()
        result = renderer.pmr1_curation()
        self.assertEqual(result, [
            {'label': u'Curation Status:', 'stars': u'1',},
        ])

    def testCurationValuesSome(self):
        self.exposure.curation = {
            u'pmr_curation_star': [u'3'], 
            u'pmr_pcenv_star': [u'2'], 
            u'pmr_cor_star': [u'1']
        }

        renderer = self.renderer()
        result = renderer.pmr1_curation()
        self.assertEqual(result, [
            {'label': u'Curation Status:', 'stars': u'3',},
            {'label': u'OpenCell:', 'stars': u'2',},
            {'label': u'COR:', 'stars': u'1',},
        ])

    def testCurationValuesAll(self):
        self.exposure.curation = {
            u'pmr_curation_star': [u'3'], 
            u'pmr_pcenv_star': [u'2'], 
            u'pmr_cor_star': [u'1'],
            u'pmr_jsim_star': [u'0'], 
        }

        renderer = self.renderer()
        result = renderer.pmr1_curation()
        self.assertEqual(result, [
            {'label': u'Curation Status:', 'stars': u'3',},
            {'label': u'OpenCell:', 'stars': u'2',},
            {'label': u'JSim:', 'stars': u'0',},
            {'label': u'COR:', 'stars': u'1',},
        ])

    def testCurationValuesOther(self):
        self.exposure.curation = {
            u'pmr_curation_star': [u'1'], 
            u'unknown1': [u'1'], 
            u'unknown2': [u'1'], 
        }

        renderer = self.renderer()
        result = renderer.pmr1_curation()
        self.assertEqual(result, [
            {'label': u'Curation Status:', 'stars': u'1',},
        ])


class TestCollabPortlet(CompleteDocTestCase):

    def renderer(self, context=None, request=None, view=None, manager=None, assignment=None):
        context = context or self.folder
        request = request or self.folder.REQUEST
        view = view or self.folder.restrictedTraverse('@@plone')
        manager = manager or getUtility(IPortletManager,
            name='plone.rightcolumn', context=self.portal)
        assignment = assignment or collab.Assignment(
            curator_uri='http://example.com')
        renderer = getMultiAdapter(
            (context, request, view, manager, assignment), IPortletRenderer)
        # Pretend this is done...
        renderer.exposure = self.portal.exposure['1']
        return renderer

    def test_render(self):
        exposure = self.portal.exposure['1']
        r = self.renderer(context=exposure,
            assignment=collab.Assignment())
        r = r.__of__(exposure)
        r.update()
        output = r.render()
        self.assertTrue(
            'To begin collaborating on this work, please use your' in output)
        self.assertTrue('dummy clone http://nohost/plone/workspace/test'
            in output)


class TestExposureFileNotesPortlet(CompleteDocTestCase):

    def renderer(self, context=None, request=None, view=None, manager=None, assignment=None):
        context = context or self.folder
        request = request or self.folder.REQUEST
        view = view or self.folder.restrictedTraverse('@@plone')
        manager = manager or getUtility(IPortletManager,
            name='plone.rightcolumn', context=self.portal)
        assignment = assignment or ExposureFileNotes.Assignment()
        renderer = getMultiAdapter(
            (context, request, view, manager, assignment), IPortletRenderer)
        # Pretend this is done...
        renderer.exposure = self.portal.exposure['1']['README']
        return renderer

    def test_render_basic(self):
        exposure = self.portal.exposure['1']
        exposurefile = ExposureFile('README')
        exposure['README'] = exposurefile
        r = self.renderer(context=exposure['README'],
            assignment=ExposureFileNotes.Assignment())
        r = r.__of__(exposure)
        r.update()
        output = r.render()
        self.assertTrue('Views Available' in output)

    def test_render_standard_note(self):
        exposure = self.portal.exposure['1']
        exposurefile = ExposureFile('README')
        exposurefile.views = ['rdfxml', 'rdfn3']
        for v in exposurefile.views:
            # implicitly create the note
            getAdapter(exposurefile, name=v)
        exposure['README'] = exposurefile
        r = self.renderer(context=exposure['README'],
            assignment=ExposureFileNotes.Assignment())
        r = r.__of__(exposure)
        r.update()
        output = r.render()
        self.assertTrue(
            'http://nohost/plone/exposure/1/README/rdfxml' in output)
        self.assertTrue(
            'http://nohost/plone/exposure/1/README/rdfn3' in output)

    def test_render_custom_links(self):
        exposure = self.portal.exposure['1']
        exposurefile = ExposureFile('README')
        exposurefile.views = ['filename_note']
        exposure['README'] = exposurefile
        note = getAdapter(exposure['README'], name='filename_note')
        note.filename = 'dir1/f1'
        r = self.renderer(context=exposure['README'],
            assignment=ExposureFileNotes.Assignment())
        r = r.__of__(exposure)
        r.update()
        output = r.render()
        self.assertFalse(
            'http://nohost/plone/exposure/1/README/filename_note' in output)
        self.assertTrue(
            '<a href="dir1/f1"></a></li>' in output)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestPortlet))
    suite.addTest(makeSuite(TestRenderer))
    suite.addTest(makeSuite(TestPMR1CurationValues))
    suite.addTest(makeSuite(TestCollabPortlet))
    suite.addTest(makeSuite(TestExposureFileNotesPortlet))
    return suite
