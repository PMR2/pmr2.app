from zope.annotation import factory
from pmr2.app.adapter import *
from pmr2.app.factory import *


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

RDFTurtleNoteFactory = factory(RawTextNote, 'rdfturtle')
RDFn3NoteFactory = factory(RawTextNote, 'rdfn3')
RDFxmlNoteFactory = factory(RawTextNote, 'rdfxml')

RDFGroupNoteFactory = factory(GroupedNote, 'rdf')
