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
from pmr2.app.workspace.interfaces import IStorage
from pmr2.app.exposure.browser.browser import ViewPageTemplateFile

from pmr2.app.exposure.portlets.base import BaseRenderer

from pmr2.app.utility.interfaces import ILatestRelatedExposureTool


class IExposureSourcePortlet(IPortletDataProvider):
    """\
    Exposure Information portlet.
    """


class Assignment(base.Assignment):
    implements(IExposureSourcePortlet)

    def __init__(self):
        pass

    @property
    def title(self):
        # XXX I am open to suggestions on a better title
        return _(u"Exposure Source")


class Renderer(BaseRenderer):
    _template = ViewPageTemplateFile('exposure_source.pt')

    def exposure_source_init(self):
        storage = zope.component.queryAdapter(self.exposure, IStorage)
        if storage:
            storage.checkout(self.exposure.commit_id)
            self.shortrev = storage.shortrev
        else:
            self.shortrev = '<unknown>'

    @memoize
    def portal_url(self):
        portal = getToolByName(self.context, 'portal_url').getPortalObject()
        return portal.absolute_url()

    @memoize
    def derive_from_uri(self):
        workspace_uri = self.workspace.absolute_url()
        manifest_uri = '%s/@@file/%s/' % (
            self.workspace.absolute_url(), self.exposure.commit_id)
        result = {
            'workspace': {
                'label': self.workspace.title_or_id(),
                'href': workspace_uri,
            },
            'manifest': {
                'label': self.shortrev,
                'href': manifest_uri,
            },
        }
        return result

    @property
    def latest_exposure(self):
        tool = zope.component.getUtility(ILatestRelatedExposureTool)
        exposures = tool.related_to_context(
            self.context)
        if not exposures:
            return
        info = next(exposures.itervalues())
        info['label'] = (
            'A more up-to-date exposure is available'
            if info['this'] else
            'A more up-to-date related exposure is available'
        )
        return info

    @memoize
    def expired(self):
        wf = getToolByName(self.exposure, 'portal_workflow')
        state = wf.getInfoFor(self.exposure, 'review_state', '')
        return state == 'expired'


class AddForm(base.AddForm):
    form_fields = form.Fields(IExposureSourcePortlet)
    label = _(u"Add Exposure Source Portlet")
    description = _(u"This portlet displays curation information about an Exposure, but using PMR1 style.")

    def create(self, data):
        return Assignment()


class EditForm(base.EditForm):
    form_fields = form.Fields(IExposureSourcePortlet)
    label = _(u"Edit Exposure Source Portlet")
    description = _(u"This portlet displays curation information about an Exposure, but using PMR1 style.")

