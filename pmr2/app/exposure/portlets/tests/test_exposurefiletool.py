import unittest

import zope.component
import zope.interface
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from plone.app.testing import logout

from plone.portlets.interfaces import IPortletType
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignment
from plone.portlets.interfaces import IPortletDataProvider
from plone.portlets.interfaces import IPortletRenderer

from pmr2.app.exposure.portlets import exposurefiletool
from pmr2.app.exposure.interfaces import IExposureFileTool

from pmr2.app.exposure.tests.layer import EXPOSURE_INTEGRATION_LAYER


@zope.interface.implementer(IExposureFileTool)
class DummyExposureFileTool(object):
    """
    Interface for exposurefiletool utilities for exposures and related objects.
    """

    label = u'Dummy Tool Link'

    def get_tool_link(self, exposure_object):
        return exposure_object.absolute_url() + '/dummy_exposurefiletool'



class TestPortlet(unittest.TestCase):

    layer = EXPOSURE_INTEGRATION_LAYER

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal.invokeFactory('Folder', 'folder')

        self.exposure = self.portal.exposure['1']

    def test_registered(self):
        portlet = zope.component.getUtility(
            IPortletType, name='pmr2.portlets.exposure_file_tool')
        self.assertEquals(
            portlet.addview, 'pmr2.portlets.exposure_file_tool')

    def test_renderer_no_utility(self):
        context = self.exposure
        request = self.request
        view = self.exposure.restrictedTraverse('@@plone')

        manager = zope.component.getUtility(IPortletManager,
            name='plone.rightcolumn', context=self.exposure)
        assignment = exposurefiletool.Assignment()
        renderer = zope.component.getMultiAdapter(
            (context, request, view, manager, assignment), IPortletRenderer)

        self.assertTrue(isinstance(renderer, exposurefiletool.Renderer))
        result = renderer.file_access_uris()
        self.assertTrue(isinstance(result, list))
        self.assertFalse(renderer.available)

    def test_renderer_registered(self):
        # register dummy utility first this time.
        dummy = DummyExposureFileTool()
        zope.component.getSiteManager().registerUtility(
            dummy, IExposureFileTool, name='dummy')

        context = self.exposure
        request = self.request
        view = self.exposure.restrictedTraverse('@@plone')

        manager = zope.component.getUtility(IPortletManager,
            name='plone.rightcolumn', context=self.exposure)
        assignment = exposurefiletool.Assignment()
        renderer = zope.component.getMultiAdapter(
            (context, request, view, manager, assignment), IPortletRenderer)

        self.assertTrue(isinstance(renderer, exposurefiletool.Renderer))
        result = renderer.file_access_uris()
        self.assertTrue(isinstance(result, list))

        result = [(i['label'], i['href']) for i in renderer.file_access_uris()]
        self.assertTrue((u'Dummy Tool Link',
            'http://nohost/plone/exposure/1/dummy_exposurefiletool') in result)

        self.assertTrue(renderer.available)
