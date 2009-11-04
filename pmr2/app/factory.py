from cStringIO import StringIO

import zope.interface
import zope.component
from zope.location import Location, locate
from Products.CMFCore.utils import getToolByName
from Products.PortalTransforms.data import datastream

from pmr2.processor.cmeta import Cmeta
from pmr2.app.interfaces import *


def name_utility(obj, event):
    """\
    Writes the name of the utility when it is registered.  Used by
    subscriber.
    """

    locate(obj, None, event.object.name)

def factory(klass):
    class _factory(Location):
        zope.interface.implements(INamedUtilBase)
        def __init__(self):
            self.title = klass.title
            self.description = klass.description
        def __call__(self, context):
            # returns instance of the annotator
            result = klass(context)
            result.__name__ = self.__name__
            result()
    # create/return instance of the factory that instantiates the 
    # classes below.
    return _factory()


class NamedUtilBase(Location):
    """\
    Class that allows a utility to be named.
    """

    zope.interface.implements(INamedUtilBase)
    title = None
    description = None

    def __init__(self, context):
        self.context = context

    @property
    def name(self):
        return self.__name__


class PortalTransformGenBase(object):
    """\
    Utilizes Portal Transform to get content.
    """

    transform = None  # define this

    def convert(self, input):
        pt = getToolByName(input, 'portal_transforms')
        stream = datastream('pt_annotation')
        pt.convert(self.transform, input, stream)
        return stream.getData()


class ExposureFileAnnotatorBase(NamedUtilBase):

    def generate(self):
        raise NotImplementedError

    def __call__(self):
        # XXX return a data struture instead
        context = self.context
        note = zope.component.getAdapter(context, name=self.name)
        data = self.generate()
        for a, v in data:
             setattr(note, a, v)
        # as this utility is registered with the same name as the view
        # that this reader/writer is for, append it the context to
        # mark the view as generated.
        views = context.views or []  # need a list
        views.append(self.name)
        # write: to generate this view, this annonator was used
        context.views = views


class PortalTransformAnnotatorBase(
        PortalTransformGenBase, ExposureFileAnnotatorBase):
    """\
    Combining PortalTransforms with the annotator.
    """


class CellML2MathMLAnnotator(PortalTransformAnnotatorBase):
    zope.interface.implements(IExposureFileAnnotator)
    transform = 'pmr2_processor_legacy_cellml2html_mathml'
    title = u'Basic MathML'
    description = u''

    def generate(self):
        input = self.context.file()
        return (
            ('text', self.convert(input).decode('utf8')),
        )

CellML2MathMLAnnotatorFactory = factory(CellML2MathMLAnnotator)


class RDFLibEFAnnotator(ExposureFileAnnotatorBase):

    def generate(self):
        input = self.context.file()
        metadata = Cmeta(StringIO(input))
        return (
            ('text', unicode(metadata.graph.serialize(format=self.format))),
        )


# DocView Generator
class ExposureFileDocViewGenBase(NamedUtilBase):
    """\
    Base utility class.
    """

    def generateTitle(self):
        raise NotImplementedError

    def generateDescription(self):
        raise NotImplementedError

    def generateText(self):
        raise NotImplementedError

    def __call__(self):
        context = self.context
        context.setTitle(self.generateTitle())
        context.setDescription(self.generateDescription())
        context.setText(self.generateText())
        context.docview_generator = self.name


class PortalTransformDocViewGenBase(
        PortalTransformGenBase, ExposureFileDocViewGenBase):
    """\
    Combining PortalTransforms with the document view generator.
    """

    def generateTitle(self):
        return u''

    def generateDescription(self):
        return u''

    def generateText(self):
        input = self.context.file()
        return self.convert(input)


class HTMLDocViewGen(PortalTransformDocViewGenBase):
    zope.interface.implements(IExposureFileDocViewGen)
    transform = 'safe_html'
    title = u'HTML annotator'
    description = u'This converts raw HTML files into a format suitable for ' \
                   'a Plone site.'

HTMLDocViewGenFactory = factory(HTMLDocViewGen)


class RSTDocViewGen(PortalTransformDocViewGenBase):
    zope.interface.implements(IExposureFileDocViewGen)
    transform = 'rest_to_html'
    title = u'reStructuredText annotator'
    description = u'This converts raw RST files into a format suitable for ' \
                   'a Plone site.'

RSTDocViewGenFactory = factory(RSTDocViewGen)
