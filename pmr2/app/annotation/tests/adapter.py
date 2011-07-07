from zope.interface import alsoProvides
from pmr2.app.factory import *
from pmr2.app.interfaces import *
from pmr2.app.annotation import note_factory
from pmr2.app.annotation.interfaces import *
from pmr2.app.annotation.annotator import RDFLibEFAnnotator
from pmr2.app.annotation.annotator import ExposureFileAnnotatorBase
from pmr2.app.annotation.note import RawTextNote
from pmr2.app.annotation.note import GroupedNote

from content import *


class RDFTurtleAnnotator(RDFLibEFAnnotator):
    zope.interface.implements(IExposureFileAnnotator)
    title = u'RDF Turtle'
    description = u'This extracts and converts a CellML with RDF (or an RDF ' \
                   'file) into Turtle format for display.'
    format = 'turtle'
    for_interface = IRawTextNote


class RDFn3Annotator(RDFLibEFAnnotator):
    zope.interface.implements(IExposureFileAnnotator)
    title = u'RDF n-Triple'
    description = u'This extracts and converts a CellML with RDF (or an RDF ' \
                   'file) into n-triple format for display.'
    format = 'n3'
    for_interface = IRawTextNote


class RDFxmlAnnotator(RDFLibEFAnnotator):
    zope.interface.implements(IExposureFileAnnotator)
    title = u'RDF xml'
    description = u'This extracts and converts a CellML with RDF (or an RDF ' \
                   'file) into xml format for display.'
    format = 'xml'
    for_interface = IRawTextNote


class Rot13NoteAnnotator(ExposureFileAnnotatorBase):
    zope.interface.implements(IExposureFileAnnotator)
    title = u'Rot13 Note'
    description = u'This is an annotator that returns rot13 of the file.'
    for_interface = IRawTextNote

    def generate(self):
        return (('text', unicode(self.input.encode('rot13'))),)


class EditedNoteAnnotator(ExposureFileAnnotatorBase):
    zope.interface.implements(IExposureFileAnnotator, 
                              IExposureFileEditAnnotator)
    title = u'Edited Note'
    description = u'This is a simple edited note annotator for testing.'
    for_interface = IEditedNote


class PostEditedNoteAnnotator(ExposureFileAnnotatorBase):
    zope.interface.implements(IExposureFileAnnotator, 
                              IExposureFilePostEditAnnotator)
    title = u'Post Edited Note'
    description = u'This is a simple edited note annotator for testing.'
    for_interface = IPostEditedNote
    edited_names = ('chars',)

    def generate(self):
        if self.note.chars is not None:
            return (('text', unicode(self.input[0:self.note.chars])),)


RDFTurtleAnnotatorFactory = named_factory(RDFTurtleAnnotator)
RDFn3AnnotatorFactory = named_factory(RDFn3Annotator)
RDFxmlAnnotatorFactory = named_factory(RDFxmlAnnotator)
# the three current types of note annotator factories.
Rot13NoteAnnotatorFactory = named_factory(Rot13NoteAnnotator)
EditedNoteAnnotatorFactory = named_factory(EditedNoteAnnotator)
PostEditedNoteAnnotatorFactory = named_factory(PostEditedNoteAnnotator)


RDFTurtleNoteFactory = note_factory(RawTextNote, 'rdfturtle')
RDFn3NoteFactory = note_factory(RawTextNote, 'rdfn3')
RDFxmlNoteFactory = note_factory(RawTextNote, 'rdfxml')
# the three current types of note content factories.
Rot13NoteFactory = note_factory(RawTextNote, 'rot13')
EditedNoteFactory = note_factory(EditedNote, 'edited_note')
PostEditedNoteFactory = note_factory(PostEditedNote, 'post_edited_note')


RDFGroupNoteFactory = note_factory(GroupedNote, 'rdf')
