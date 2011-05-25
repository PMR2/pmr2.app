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


class Renderer(base.Renderer):
    _template = ViewPageTemplateFile('exposure_source.pt')

    def __init__(self, *args):
        base.Renderer.__init__(self, *args)
        self.title = u'Curation'
        if self.available:
            values = zope.component.getAdapter(
                self.context, IExposureSourceAdapter).source()
            self.exposure, self.workspace, self.path = values
            storage = zope.component.getAdapter(self.exposure, IStorage)
            storage.checkout(self.exposure.commit_id)
            self.shortrev = storage.shortrev

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
                'label': self.workspace.Title,
                'href': workspace_uri,
            },
            'manifest': {
                'label': self.shortrev,
                'href': manifest_uri,
            },
        }
        return result

    @property
    def available(self):
        return IExposureObject.providedBy(self.context)

    @memoize
    def expired(self):
        wf = getToolByName(self.exposure, 'portal_workflow')
        state = wf.getInfoFor(self.exposure, 'review_state', '')
        return state == 'expired'

    def render(self):
        return self._template()


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

