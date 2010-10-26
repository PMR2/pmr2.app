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


class IExposureInfoPortlet(IPortletDataProvider):
    """\
    Exposure Information portlet.
    """


class Assignment(base.Assignment):
    implements(IExposureInfoPortlet)

    def __init__(self):
        pass

    @property
    def title(self):
        # XXX I am open to suggestions on a better title
        return _(u"Exposure Info")


class Renderer(base.Renderer):
    _template = ViewPageTemplateFile('exposure_info.pt')

    def __init__(self, *args):
        base.Renderer.__init__(self, *args)
        self.title = 'Exposure Info'
        if self.available:
            values = zope.component.getAdapter(
                self.context, IExposureSourceAdapter).source()
            self.exposure, self.workspace, self.path  = values

    @property
    def links(self):
        result = []
        for view in self.context.views:
            result.append({
                'href': '%s/@@%s' % (self.context.absolute_url(), view),
                'title': view,
            })
        return result

    @memoize
    def portal_url(self):
        portal = getToolByName(self.context, 'portal_url').getPortalObject()
        return portal.absolute_url()

    @memoize
    def pmr1_curation(self):
        """
        Temporary method for PMR1 compatibility styles.
        """

        pairs = (
            ('pmr_curation_star', u'Curation Status:'),
            ('pmr_pcenv_star', u'OpenCell:'),
            ('pmr_jsim_star', u'JSim:'),
            ('pmr_cor_star', u'COR:'),
        )
        curation = self.exposure.curation or {}
        result = []
        for key, label in pairs:
            # first item or character
            stars = key in curation and curation[key][0] or u'0'
            result.append({
                'label': label,
                'stars': stars,
            })
        return result

    @memoize
    def derive_from_uri(self):
        workspace_uri = self.workspace.absolute_url()
        manifest_uri = '%s/@@file/%s/' % (
            self.workspace.absolute_url(), self.exposure.commit_id)
        result = {
            'workspace': {
                'label': self.workspace.Title,
                'href': workspace_uri,
            },
            'manifest': {
                'label': short(self.context.commit_id),
                'href': manifest_uri,
            },
        }
        return result

    @memoize
    def file_access_uris(self):
        result = []
        archive_uri = '%s/@@archive/%s/gz' % (
            self.workspace.absolute_url(), self.exposure.commit_id)
        result.append({
            'label': u'Complete Model (as .tgz)', 'href': archive_uri})
        if IExposureFile.providedBy(self.context):
            file_uri = '%s/@@rawfile/%s/%s' % (
                self.workspace.absolute_url(),
                self.exposure.commit_id,
                self.path
            )
            result.append({
                'label': u'This File', 'href': file_uri})
        return result

    @property
    def available(self):
        return IExposureObject.providedBy(self.context)

    def render(self):
        return self._template()


class AddForm(base.AddForm):
    form_fields = form.Fields(IExposureInfoPortlet)
    label = _(u"Add Exposure Info Portlet")
    description = _(u"This portlet displays information about an Exposure.")

    def create(self, data):
        return Assignment()


class EditForm(base.EditForm):
    form_fields = form.Fields(IExposureInfoPortlet)
    label = _(u"Edit Exposure Info Portlet")
    description = _(u"This portlet displays information about an Exposure.")
