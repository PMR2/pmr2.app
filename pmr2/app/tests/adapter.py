from zope.interface import alsoProvides
import zope.annotation
from pmr2.app.adapter import *
from pmr2.app.factory import *
from pmr2.app.interfaces import *
from pmr2.app.annotation.annotator import RDFLibEFAnnotator
from pmr2.app.annotation.note import RawTextNote
from pmr2.app.annotation.note import GroupedNote


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

RDFTurtleAnnotatorFactory = named_factory(RDFTurtleAnnotator)
RDFn3AnnotatorFactory = named_factory(RDFn3Annotator)
RDFxmlAnnotatorFactory = named_factory(RDFxmlAnnotator)


RDFTurtleNoteFactory = zope.annotation.factory(RawTextNote, 'rdfturtle')
RDFn3NoteFactory = zope.annotation.factory(RawTextNote, 'rdfn3')
RDFxmlNoteFactory = zope.annotation.factory(RawTextNote, 'rdfxml')

RDFGroupNoteFactory = zope.annotation.factory(GroupedNote, 'rdf')
