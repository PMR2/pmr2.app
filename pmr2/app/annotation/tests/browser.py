from pmr2.app.exposure.browser.browser import GroupedNoteViewBase
from pmr2.app.exposure.browser.browser import ExposureFileViewBase


class RdfGroupedNote(GroupedNoteViewBase):
    subtitle=u'RDF views available'
    choices={
        u'turtle': u'rdfturtle', 
        u'n3': u'rdfn3', 
        u'xml': u'rdfxml',
    }


class EditedNote(ExposureFileViewBase):

    def __call__(self):
        return 'Edited Note is: [%s]' % self.note.note


class PostEditedNote(ExposureFileViewBase):

    def __call__(self):
        return 'Post Edited Note is: [%d:%s]' % (
            self.note.chars, self.note.text)
