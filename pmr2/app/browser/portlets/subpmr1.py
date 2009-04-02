from zope import schema
from zope.component import getMultiAdapter
from zope.formlib import form
from zope.interface import implements

from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.cache import render_cachekey

from Acquisition import aq_inner
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFPlone import PloneMessageFactory as _


class ISubPMR1Portlet(IPortletDataProvider):
    """\
    PMR1 Metadoc portlet.
    """


class Assignment(base.Assignment):
    implements(ISubPMR1Portlet)

    def __init__(self):
        pass

    @property
    def title(self):
        return _(u"Sub pages")


class Renderer(base.Renderer):
    _template = ViewPageTemplateFile('subpmr1.pt')

    def __init__(self, *args):
        base.Renderer.__init__(self, *args)

        context = aq_inner(self.context)
        portal_state = getMultiAdapter((context, self.request), name=u'plone_portal_state')
        self.portal_url = portal_state.portal_url()
        self.typesToShow = portal_state.friendly_types()

        plone_tools = getMultiAdapter((context, self.request), name=u'plone_tools')
        self.catalog = plone_tools.catalog()

        if self.available:
            struct = self.context.get_subdocument_structure()
            self._title = struct['title']
            self._subdocs = struct['subdocs']
        
    def title(self):
        return self._title

    def render(self):
        return self._template()

    @property
    def available(self):
        if hasattr(self, '_struct'):
            return self._struct is not None
        self._struct = None
        # XXX should deal with interface here that will implement this
        # method
        if hasattr(self.context, 'get_subdocument_structure'):
            self._struct = self.context.get_subdocument_structure()
        return self._struct is not None

    def subdocument(self):
        return self._subdocs


class AddForm(base.AddForm):
    form_fields = form.Fields(ISubPMR1Portlet)
    label = _(u"Add PMR1 Exposure Portlet")
    description = _(u"This portlet displays list of PMR1 Metadoc subcontents.")

    def create(self, data):
        return Assignment()


class EditForm(base.EditForm):
    form_fields = form.Fields(ISubPMR1Portlet)
    label = _(u"Edit PMR1 Exposure Portlet")
    description = _(u"This portlet displays list of PMR1 Metadoc subcontents.")
