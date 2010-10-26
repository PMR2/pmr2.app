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
from pmr2.app.exposure.interfaces import *
from pmr2.app.browser.page import ViewPageTemplateFile
from pmr2.app.util import short


class IExposureDownloadPortlet(IPortletDataProvider):
    """\
    Exposure Information portlet.
    """


class Assignment(base.Assignment):
    implements(IExposureDownloadPortlet)

    def __init__(self):
        pass

    @property
    def title(self):
        # XXX I am open to suggestions on a better title
        return _(u"Exposure Download")


class Renderer(base.Renderer):
    _template = ViewPageTemplateFile('exposure_download.pt')

    def __init__(self, *args):
        base.Renderer.__init__(self, *args)
        self.title = u'Curation'
        if self.available:
            values = zope.component.getAdapter(
                self.context, IExposureSourceAdapter).source()
            self.exposure, self.workspace, self.path = values

    @memoize
    def portal_url(self):
        portal = getToolByName(self.context, 'portal_url').getPortalObject()
        return portal.absolute_url()

    def view_url(self, view='rawfile'):
        return '%s/@@%s/%s/%s' % (
            self.workspace.absolute_url(),
            view,
            self.exposure.commit_id,
            self.path
        )

    # labels may change, so commenting this out for now
    #@memoize
    def file_access_uris(self):
        result = []
        archive_uri = '%s/@@archive/%s/gz' % (
            self.workspace.absolute_url(), self.exposure.commit_id)
        result.append({
            'label': u'Complete Archive as .tgz', 'href': archive_uri})
        if IExposureFile.providedBy(self.context):
            result.append({
                'label': u'Download This File',
                'href': self.view_url(),
            })
        return result

    @property
    def available(self):
        return IExposureObject.providedBy(self.context)

    def render(self):
        return self._template()


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

