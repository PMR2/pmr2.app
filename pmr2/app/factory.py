from cStringIO import StringIO

import zope.interface
import zope.component
from zope.location import Location, locate
from Products.CMFCore.utils import getToolByName
from Products.PortalTransforms.data import datastream

from pmr2.processor.cmeta import Cmeta
from pmr2.app.interfaces import IExposureFileAnnotator
from pmr2.app.interfaces import IExposureFileViewUtility


def name_utility(obj, event):
    # writes the name of the annotator is registered under into the 
    # annotator
    locate(obj, None, event.object.name)


class ExposureFileAnnotatorBase(Location):

    def generate(self, context):
        raise NotImplementedError

    @property
    def annotator(self):
        if not hasattr(self, '__annotator'):
            self.__annotator = zope.component.getUtility(
                IExposureFileAnnotator, name=self.__name__)
        return self.__annotator

    def read(self, context):
        """\
        Parse the context into an object with the required fields.
        """

        result = zope.component.queryAdapter(context, name=self.__name__)
        return result

    def write(self, context):
        # XXX return a data struture instead
        note = zope.component.queryAdapter(context, name=self.__name__)
        data = self.generate(context)
        for a, v in data:
             setattr(note, a, v)
        # as this utility is registered with the same name as the view
        # that this reader/writer is for, append it the context to
        # mark the view as generated.
        views = context.views or []  # need a list
        views.append(self.__name__)
        # write: to generate this view, this annonator was used
        context.views = views


class ExposureFileDocViewGenBase(object):
    """\
    This generator assigns result value for the default document view.
    """

    def generate(self, context):
        raise NotImplementedError

    def write(self, context):
        result = self.generate(context)
        context.setText(output)


class PortalTransformAnnotatorBase(ExposureFileDocViewGenBase):
    """\
    Utilizes Portal Transform to get content.  By default it tries to
    turn files into HTML.
    """

    transform = None  # define this

    def convert(self, input):
        pt = getToolByName(input, 'portal_transforms')
        stream = datastream('pt_annotation')
        pt.convert(self.transform, input, stream)
        return stream.getData()

    def generate(self, context):
        # standard way is to assign the text field of context
        input = context.file()
        return self.convert(input)


class HTMLAnnotator(PortalTransformAnnotatorBase):
    zope.interface.implements(IExposureFileAnnotator)
    transform = 'safe_html'
    title = u'HTML annotator'
    description = u'This converts raw HTML files into a format suitable for ' \
                   'a Plone site.'


class RSTAnnotator(PortalTransformAnnotatorBase):
    zope.interface.implements(IExposureFileAnnotator)
    transform = 'rest_to_html'
    title = u'reStructuredText annotator'
    description = u'This converts raw RST files into a format suitable for ' \
                   'a Plone site.'

class RDFLibEFAnnotator(ExposureFileAnnotatorBase):

    def generate(self, context):
        input = context.file()
        metadata = Cmeta(StringIO(input))
        return (
            ('text', unicode(metadata.graph.serialize(format=self.format))),
        )

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
