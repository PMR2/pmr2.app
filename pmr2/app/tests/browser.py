from plone.z3cform import layout
from pmr2.app.browser.exposure import GroupedNoteViewBase
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
