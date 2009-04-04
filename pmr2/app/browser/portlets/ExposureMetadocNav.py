from zope import schema
from zope.component import getMultiAdapter
from zope.formlib import form
from zope.interface import implements

from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.cache import render_cachekey

from Acquisition import aq_inner, aq_parent
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFPlone import PloneMessageFactory as _

from pmr2.app.content import Exposure


class IExposureMetadocNavPortlet(IPortletDataProvider):
    """\
    Exposure Metadoc Listing Portlet.
    """


class Assignment(base.Assignment):
    implements(IExposureMetadocNavPortlet)

    def __init__(self):
        pass

    @property
    def title(self):
        return _(u"Exposure Subpages")


class Renderer(base.Renderer):
    _template = ViewPageTemplateFile('exposure_metadoc_nav.pt')

    def __init__(self, *args):
        base.Renderer.__init__(self, *args)

        context = aq_inner(self.context)
        portal_state = getMultiAdapter((context, self.request), name=u'plone_portal_state')
        self.portal_url = portal_state.portal_url()
        self.typesToShow = portal_state.friendly_types()

        plone_tools = getMultiAdapter((context, self.request), name=u'plone_tools')
        self.catalog = plone_tools.catalog()

        container = self.findExposure()
        if not container:
            self._available = False
            self.results = []
        else:
            path = container.absolute_url_path()
            self.root_url = container.absolute_url()
            self.results = self.catalog(
                # XXX really should go for implemented interface
                portal_type='ExposurePMR1Metadoc', 
                path=path,
                sort_on='sortable_title',
            )

        self.title = 'Exposure Subpages'

    def findExposure(self):
        o = aq_inner(self.context)
        while o:
            if isinstance(o, Exposure):
                return o
            o = aq_parent(o)

    def render(self):
        return self._template()

    @property
    def available(self):
        if hasattr(self, '_available'):
            return self._available
        return True

    def subdocument(self):
        return self._subdocs


class AddForm(base.AddForm):
    form_fields = form.Fields(IExposureMetadocNavPortlet)
    label = _(u"Add Exposure Metadoc Navigation Portlet")
    description = _(u"This portlet displays list of Exposures metadoc pages within an Exposure.")

    def create(self, data):
        return Assignment()


class EditForm(base.EditForm):
    form_fields = form.Fields(IExposureMetadocNavPortlet)
    label = _(u"Edit Exposure Metadoc Navigation Portlet")
    description = _(u"This portlet displays list of Exposures metadoc pages within an Exposure.")
