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

from pmr2.app.content import ExposureContainer

# XXX this could be replaced with a standard collection.

class IExposureNavPortlet(IPortletDataProvider):
    """\
    Exposure Navigation Portlet.
    """


class Assignment(base.Assignment):
    implements(IExposureNavPortlet)

    def __init__(self):
        pass

    @property
    def title(self):
        # name of the portlet in the manager
        return _(u"Exposure Listing")


class Renderer(base.Renderer):
    _template = ViewPageTemplateFile('exposure_nav.pt')

    def __init__(self, *args):
        base.Renderer.__init__(self, *args)

        context = aq_inner(self.context)
        portal_state = getMultiAdapter((context, self.request), name=u'plone_portal_state')
        self.portal_url = portal_state.portal_url()
        self.typesToShow = portal_state.friendly_types()

        plone_tools = getMultiAdapter((context, self.request), name=u'plone_tools')
        self.catalog = plone_tools.catalog()

        container = self.findExposureContainer()
        if not container:
            self._available = False
            self.results = []
        else:
            path = '/'.join(container.getPhysicalPath())
            self.root_url = container.absolute_url()
            self.results = self.catalog(
                portal_type='Exposure', 
                path=path,
                sort_on='sortable_title',
            )

        # portlet title for users
        self.title = 'Exposure Listing'

    def findExposureContainer(self):
        o = aq_inner(self.context)
        while o is not None:
            if isinstance(o, ExposureContainer):
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
    form_fields = form.Fields(IExposureNavPortlet)
    label = _(u"Add Exposure Navigation Portlet")
    description = _(u"This portlet displays list of Exposures in the container.")

    def create(self, data):
        return Assignment()


class EditForm(base.EditForm):
    form_fields = form.Fields(IExposureNavPortlet)
    label = _(u"Edit Exposure Navigation Portlet")
    description = _(u"This portlet displays list of Exposures in the container.")
