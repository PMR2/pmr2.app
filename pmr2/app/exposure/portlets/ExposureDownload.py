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
        return _(u"Exposure Download (legacy)")


class Renderer(BaseRenderer):
    _template = ViewPageTemplateFile('exposure_download.pt')

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
        # XXX should refer this to the more verbose download option
        # page when this is added to the workspace.
        result = []
        # XXX a utility should be created to test whether this option is
        # implemented for the storage at hand
        archive_uri = '%s/@@archive/%s/tgz' % (
            self.workspace.absolute_url(), self.exposure.commit_id)
        result.append({
            'label': u'Complete Archive as .tgz', 'href': archive_uri})
        if IExposureFile.providedBy(self.context):
            result.append({
                'label': u'Download This File',
                'href': self.view_url(),
            })

        archivers = zope.component.getUtilitiesFor(IStorageArchiver)
        storage = IStorage(self.exposure)
        archive_uri = '%s/@@archive/%s/%s'
        for name, a in archivers:
            if a.enabledFor(storage):
                result.append({'label': a.label, 'href': archive_uri % (
                    self.workspace.absolute_url(),
                    self.exposure.commit_id,
                    name,
                )})
        return result


class AddForm(base.AddForm):
    form_fields = form.Fields(IExposureDownloadPortlet)
    label = _(u"Add Exposure Download Portlet (legacy)")
    description = _(u"Lists legacy download options for this Exposure object.")

    def create(self, data):
        return Assignment()


class EditForm(base.EditForm):
    form_fields = form.Fields(IExposureDownloadPortlet)
    label = _(u"Edit Exposure Download Portlet (legacy)")
    description = _(u"Lists legacy download options for this Exposure object.")

