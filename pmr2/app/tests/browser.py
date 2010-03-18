import os.path
from z3c.form import tests
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from plone.z3cform import layout
from pmr2.app.browser.exposure import GroupedNoteViewBase
from pmr2.app.browser.exposure import ExposureFileViewBase
from pmr2.app.browser.layout import PlainLayoutWrapper


class RdfGroupedNote(GroupedNoteViewBase):
    subtitle=u'RDF views available'
    choices={
        u'turtle': u'rdfturtle', 
        u'n3': u'rdfn3', 
        u'xml': u'rdfxml',
    }

RdfGroupedNoteView = layout.wrap_form(RdfGroupedNote, 
    __wrapper_class=PlainLayoutWrapper,
)


class EditedNoteView(ExposureFileViewBase):

    def __call__(self):
        return 'Edited Note is: [%s]' % self.note.note


class PostEditedNoteView(ExposureFileViewBase):

    def __call__(self):
        return 'Post Edited Note is: [%d:%s]' % (
            self.note.chars, self.note.text)


class GroupTemplate(object):

    def __init__(self, context):
        self.context = context

    def __call__(self):
        return ViewPageTemplateFile('simple_groupedit.pt', os.path.dirname(
            tests.__file__))(self.context)
