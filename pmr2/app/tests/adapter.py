from zope.interface import alsoProvides
from pmr2.app.adapter import *
from pmr2.app.factory import *
from pmr2.app.interfaces import *
from pmr2.app.annotation import note_factory
from pmr2.app.annotation.interfaces import *
from pmr2.app.annotation.annotator import RDFLibEFAnnotator
from pmr2.app.annotation.annotator import ExposureFileEditableAnnotatorBase
from pmr2.app.annotation.note import RawTextNote
from pmr2.app.annotation.note import GroupedNote

from content import EditedNote


class RDFTurtleAnnotator(RDFLibEFAnnotator):
    zope.interface.implements(IExposureFileAnnotator)
    title = u'RDF Turtle'
    description = u'This extracts and converts a CellML with RDF (or an RDF ' \
                   'file) into Turtle format for display.'
    format = 'turtle'


class RDFn3Annotator(RDFLibEFAnnotator):
    zope.interface.implements(IExposureFileAnnotator)
    title = u'RDF n-Triple'
    description = u'This extracts and converts a CellML with RDF (or an RDF ' \
                   'file) into n-triple format for display.'
    format = 'n3'


class RDFxmlAnnotator(RDFLibEFAnnotator):
    zope.interface.implements(IExposureFileAnnotator)
    title = u'RDF xml'
    description = u'This extracts and converts a CellML with RDF (or an RDF ' \
                   'file) into xml format for display.'
    format = 'xml'

class EditedNoteAnnotator(ExposureFileEditableAnnotatorBase):
    zope.interface.implements(IExposureFileAnnotator)
    title = u'Edited Note'
    description = u'This is a simple edited note annotator for testing.'


RDFTurtleAnnotatorFactory = named_factory(RDFTurtleAnnotator)
RDFn3AnnotatorFactory = named_factory(RDFn3Annotator)
RDFxmlAnnotatorFactory = named_factory(RDFxmlAnnotator)
EditedNoteAnnotatorFactory = named_factory(EditedNoteAnnotator)


RDFTurtleNoteFactory = note_factory(RawTextNote, 'rdfturtle')
RDFn3NoteFactory = note_factory(RawTextNote, 'rdfn3')
RDFxmlNoteFactory = note_factory(RawTextNote, 'rdfxml')
EditedNoteFactory = note_factory(EditedNote, 'edited_note')

RDFGroupNoteFactory = note_factory(GroupedNote, 'rdf')
