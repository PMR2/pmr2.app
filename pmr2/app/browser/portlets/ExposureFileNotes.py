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

from pmr2.app.interfaces import IExposureFile


class IExposureFileNotesPortlet(IPortletDataProvider):
    """\
    Exposure File Notes Listing Portlet.

    This is for ExposureFile objects
    """


class Assignment(base.Assignment):
    implements(IExposureFileNotesPortlet)

    def __init__(self):
        pass

    @property
    def title(self):
        # XXX I am open to suggestions on a better title
        return _(u"Exposure File Notes")


class Renderer(base.Renderer):
    _template = ViewPageTemplateFile('exposure_file_notes.pt')

    def __init__(self, *args):
        base.Renderer.__init__(self, *args)
        self.title = 'Exposure File Notes'

    @property
    def links(self):
        result = []
        for view in self.context.views:
            result.append({
                'href': '%s/@@%s' % (self.context.absolute_url(), view),
                'title': view,
            })
        return result

    def render(self):
        return self._template()

    @property
    def available(self):
        return IExposureFile.providedBy(self.context)


class AddForm(base.AddForm):
    form_fields = form.Fields(IExposureFileNotesPortlet)
    label = _(u"Add Exposure File Notes Portlet")
    description = _(u"This portlet displays the list of Notes attached to " \
                     "the Exposure File.")

    def create(self, data):
        return Assignment()


class EditForm(base.EditForm):
    form_fields = form.Fields(IExposureFileNotesPortlet)
    label = _(u"Edit Exposure File Notes Portlet")
    description = _(u"This portlet displays the list of Notes attached to " \
                     "the Exposure File.")
