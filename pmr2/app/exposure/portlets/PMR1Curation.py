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


class IPMR1CurationPortlet(IPortletDataProvider):
    """\
    Exposure Information portlet.
    """


class Assignment(base.Assignment):
    implements(IPMR1CurationPortlet)

    def __init__(self):
        pass

    @property
    def title(self):
        return _(u"Model Curation")


class Renderer(base.Renderer):
    _template = ViewPageTemplateFile('pmr1_curation.pt')

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
        required = ['pmr_curation_star']
        curation = self.exposure.curation or {}
        result = []
        for key, label in pairs:
            # first item or character
            stars = key in curation and curation[key][0] or None
            if key in required:
                stars = stars or u'0'
            if stars is not None:
                result.append({
                    'label': label,
                    'stars': stars,
                })
        return result

    @property
    def available(self):
        return IExposureObject.providedBy(self.context)

    def render(self):
        return self._template()


class AddForm(base.AddForm):
    form_fields = form.Fields(IPMR1CurationPortlet)
    label = _(u"Add PMR1 Curation Portlet")
    description = _(u"This portlet displays curation information about an Exposure, but using PMR1 style.")

    def create(self, data):
        return Assignment()


class EditForm(base.EditForm):
    form_fields = form.Fields(IPMR1CurationPortlet)
    label = _(u"Edit PMR1 Curation Portlet")
    description = _(u"This portlet displays curation information about an Exposure, but using PMR1 style.")

