from zope import schema
from zope.formlib import form
from zope.interface import implements
import zope.component

from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.cache import render_cachekey
from plone.memoize.view import memoize

from Acquisition import aq_inner, aq_parent
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFCore.utils import getToolByName

from pmr2.app.interfaces import *
from pmr2.app.workspace.interfaces import IStorage, IStorageArchiver
from pmr2.app.exposure.interfaces import *
from pmr2.app.exposure.browser.browser import ViewPageTemplateFile

from pmr2.app.exposure.portlets.base import BaseRenderer


class IExposureDownloadPortlet(IPortletDataProvider):
    """
    Exposure download portlet.
    """


class Assignment(base.Assignment):
    implements(IExposureDownloadPortlet)

    def __init__(self):
        pass

    @property
    def title(self):
        # XXX I am open to suggestions on a better title
        return _(u"Exposure Download")


class Renderer(BaseRenderer):
    _template = ViewPageTemplateFile('exposure_download.pt')

    @memoize
    def portal_url(self):
        portal = getToolByName(self.context, 'portal_url').getPortalObject()
        return portal.absolute_url()

    def file_access_uris(self):
        tools = zope.component.getUtilitiesFor(IExposureDownloadTool)
        results = []
        for name, tool in sorted(tools):
            link = tool.get_download_link(self.context)
            if not link:
                continue
            results.append({'label': tool.label, 'href': link})
        return results


class AddForm(base.AddForm):
    form_fields = form.Fields(IExposureDownloadPortlet)
    label = _(u"Add Exposure Download Portlet")
    description = _(u"This portlet displays curation information about an Exposure, but using PMR1 style.")

    def create(self, data):
        return Assignment()


class EditForm(base.EditForm):
    form_fields = form.Fields(IExposureDownloadPortlet)
    label = _(u"Edit Exposure Download Portlet")
    description = _(u"This portlet displays curation information about an Exposure, but using PMR1 style.")

