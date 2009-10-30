from cStringIO import StringIO

import zope.interface
from Products.CMFCore.utils import getToolByName
from Products.PortalTransforms.data import datastream

from pmr2.processor.cmeta import Cmeta
from pmr2.app.interfaces import IExposureFileAnnotator

class ExposureFileAnnotatorBase(object):

    def generate(self):
        raise NotImplementedError

    def __call__(self, context):
        name = self.adapter
        # assert context implements IExposureFile?
        self.context = context
        # let subclasses know not to muck with this
        self.__annotation = zope.component.queryAdapter(context, name=name)
        # shouldn't really have to muck around with this either
        self._input = self.context.file()
        self.generate()
        # we are done, let the adapters be added
        if name not in context.adapters:
            a = context.adapters
            a.append(name)
            context.adapters = a

    @property
    def input(self):
        if not hasattr(self, '_input'):
            self._input = self.context.file()
        return self._input

    @property
    def annotation(self):
        return self.__annotation


class PortalTransformAnnotator(ExposureFileAnnotatorBase):
    """\
    Utilizes Portal Transform to get content.  By default it tries to
    turn files into HTML.
    """

    # not implementing this because this is an incomplete tool.
    #zope.interface.implements(IExposureFileAnnotator)
    adapter = 'StandardExposureFile'
    transform = None  # define this

    def convert(self):
        pt = getToolByName(self.context, 'portal_transforms')
        stream = datastream('pt_annotation')
        pt.convert(self.transform, self.input, stream)
        return stream.getData()

    def generate(self):
        # standard way is to assign the text field of context
        output = self.convert()
        self.context.setText(output)


class HTMLAnnotator(PortalTransformAnnotator):
    zope.interface.implements(IExposureFileAnnotator)
    transform = 'safe_html'
    title = u'HTML annotator'
    description = u'This converts raw HTML files into a format suitable for ' \
                   'a Plone site.'


class RSTAnnotator(PortalTransformAnnotator):
    zope.interface.implements(IExposureFileAnnotator)
    transform = 'rest_to_html'
    title = u'reStructuredText annotator'
    description = u'This converts raw RST files into a format suitable for ' \
                   'a Plone site.'


class RDFTurtleAnnotator(ExposureFileAnnotatorBase):
    zope.interface.implements(IExposureFileAnnotator)
    adapter = 'RDFTurtle'
    title = u'RDF Turtle'
    description = u'This extracts and converts a CellML with RDF (or an RDF ' \
                   'file into Turtle format for display.'

    def generate(self):
        metadata = Cmeta(StringIO(self.input))
        self.annotation.text = unicode(
            metadata.graph.serialize(format='turtle'))
