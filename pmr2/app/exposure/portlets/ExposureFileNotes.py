import zope.schema
import zope.component
from zope.formlib import form
from zope.interface import implements

from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.cache import render_cachekey

from Acquisition import aq_inner, aq_parent
from Products.CMFPlone import PloneMessageFactory as _

from pmr2.app.exposure.interfaces import IExposureFile
from pmr2.app.annotation.interfaces import IExposureNoteTarget
from pmr2.app.annotation.factory import has_note
from pmr2.app.annotation.factory import default_note_url
from pmr2.app.exposure.browser.browser import ViewPageTemplateFile


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

    @property
    def links(self):
        vocab = zope.component.queryUtility(
            zope.schema.interfaces.IVocabulary,
            name='pmr2.vocab.ExposureFileAnnotators'
        )

        result = [
            {
                'href': zope.component.queryAdapter(
                    self.context, IExposureNoteTarget, name=view,
                    default=default_note_url(self.context))(view),
                'title': vocab.getTerm(view).title,
            }
            for view in self.context.views if 
                has_note(self.context, view) and
                not view in self.context.hidden_views
        ]
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
