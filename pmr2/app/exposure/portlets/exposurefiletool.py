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

from pmr2.app.workspace.interfaces import IStorage, IStorageArchiver
from pmr2.app.exposure.interfaces import IExposureFileTool
from pmr2.app.exposure.browser.browser import ViewPageTemplateFile

from pmr2.app.exposure.portlets.base import BaseRenderer


class IToolPortlet(IPortletDataProvider):
    """
    Tools for an Exposure File
    """


class Assignment(base.Assignment):
    implements(IToolPortlet)

    def __init__(self):
        pass

    @property
    def title(self):
        return _(u"Exposure File Tool Portlet")


class Renderer(BaseRenderer):
    _template = ViewPageTemplateFile('exposure_tool.pt')

    def __init__(self, *a, **kw):
        super(Renderer, self).__init__(*a, **kw)
        self.tool_info = self.generate_tool_info()

    def _available(self):
        return (BaseRenderer._available(self) and self.tool_info)

    @memoize
    def portal_url(self):
        portal = getToolByName(self.context, 'portal_url').getPortalObject()
        return portal.absolute_url()

    def file_access_uris(self):
        return self.tool_info

    def generate_tool_info(self):
        tools = zope.component.getUtilitiesFor(IExposureFileTool)
        results = []
        for name, tool in sorted(tools):
            link = tool.get_tool_link(self.context)
            if not link:
                continue
            results.append({'label': tool.label, 'href': link})
        return results


class AddForm(base.AddForm):
    form_fields = form.Fields(IToolPortlet)
    label = _(u"Add Exposure File Tool Portlet")
    description = _(u"This portlet displays available tools for the exposure "
        "files being viewed, based on the modules installed onto this "
        "instance of PMR2.")

    def create(self, data):
        return Assignment()


class EditForm(base.EditForm):
    form_fields = form.Fields(IToolPortlet)
    label = _(u"Edit Exposure File Tool Portlet")
    description = _(u"This portlet displays available tools for the exposure "
        "files being viewed, based on the modules installed onto this "
        "instance of PMR2.")
