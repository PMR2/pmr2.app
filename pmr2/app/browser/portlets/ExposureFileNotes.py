import zope.schema
import zope.component
from zope.formlib import form
from zope.interface import implements

from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.cache import render_cachekey

from Acquisition import aq_inner, aq_parent
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFPlone import PloneMessageFactory as _

from pmr2.app.content.interfaces import IExposureFile
from pmr2.app.annotation.factory import has_note


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
        self.title = 'Views available'

    @property
    def links(self):
        vocab = zope.component.queryUtility(zope.schema.interfaces.IVocabulary,
                                            name='ExposureFileAnnotatorVocab')
        result = [{
            'href': '%s/@@%s' % (self.context.absolute_url(), view),
            'title': vocab.getTerm(view).title,
        } for view in self.context.views if has_note(self.context, view)]
        return result

    def render(self):
        return self._template()

    @property
    def available(self):
        return IExposureFile.providedBy(self.context) and self.context.views


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
