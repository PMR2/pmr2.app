from zope import schema
from zope.formlib import form
from zope.interface import implements
import zope.component

from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.cache import render_cachekey
from plone.memoize.view import memoize

from Acquisition import aq_inner, aq_parent
# XXX change this i18n to something specific to pmr2.app.exposure
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFCore.utils import getToolByName

from pmr2.app.interfaces import *
from pmr2.app.exposure.interfaces import *
from pmr2.app.exposure.browser.browser import ViewPageTemplateFile


class IPMR1CurationPortlet(IPortletDataProvider):
    """\
    Exposure Information portlet.
    """

    curator_uri = zope.schema.ASCIILine(
        title=_(u'Curator contact'),
        description=_(u'The URI where the curator can be contacted.'),
        required=False,
    )

    # XXX to faciliate easy modification...
    contact_label = zope.schema.TextLine(
        title=_(u'Contact text'),
        description=_(u'The text label for the curator contact.'),
        default=u'Report curation issue.',
        required=False,
    )


class Assignment(base.Assignment):
    implements(IPMR1CurationPortlet)

    curator_uri = schema.fieldproperty.FieldProperty(
        IPMR1CurationPortlet['curator_uri'])
    contact_label = schema.fieldproperty.FieldProperty(
        IPMR1CurationPortlet['contact_label'])

    def __init__(self, curator_uri='', contact_label=u''):
        if curator_uri:
            self.curator_uri = curator_uri
        if contact_label:
            self.contact_label = contact_label

    @property
    def title(self):
        return _(u"Model Curation")


class Renderer(base.Renderer):
    _template = ViewPageTemplateFile('pmr1_curation.pt')

    exposure = None
    workspace = None
    path = None

    def __init__(self, *args):
        base.Renderer.__init__(self, *args)
        self.title = u'Curation'

    def update(self):
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
        curation = self.exposure is not None and self.exposure.curation or {}
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
        return Assignment(**data)


class EditForm(base.EditForm):
    form_fields = form.Fields(IPMR1CurationPortlet)
    label = _(u"Edit PMR1 Curation Portlet")
    description = _(u"This portlet displays curation information about an Exposure, but using PMR1 style.")

