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


class ExposureFileAnnotatorBase(Location):

    def generate(self, context):
        raise NotImplementedError

    def __call__(self, context):
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


class PortalTransformAnnotatorBase(
        PortalTransformGenBase, ExposureFileAnnotatorBase):
    """\
    Combining PortalTransforms with the annotator.
    """


class CellML2MathMLAnnotator(PortalTransformAnnotatorBase):
    zope.interface.implements(IExposureFileAnnotator)
    transform = 'pmr2_processor_legacy_cellml2html_mathml'
    title = u'Basic MathML'

    def generate(self, context):
        input = context.file()
        return (
            ('text', self.convert(input).decode('utf8')),
        )


class RDFLibEFAnnotator(ExposureFileAnnotatorBase):

    def generate(self, context):
        input = context.file()
        metadata = Cmeta(StringIO(input))
        return (
            ('text', unicode(metadata.graph.serialize(format=self.format))),
        )


# DocView Generator
class ExposureFileDocViewGenBase(object):
    """\
    Base utility class.
    """

    def generateTitle(self, context):
        raise NotImplementedError

    def generateDescription(self, context):
        raise NotImplementedError

    def generateText(self):
        raise NotImplementedError

    def __call__(self, context):
        context.setTitle(self.generateTitle(context))
        context.setDescription(self.generateDescription(context))
        context.setText(self.generateText(context))
        context.docview_generator = self.__name__


class PortalTransformDocViewGenBase(
        PortalTransformGenBase, ExposureFileDocViewGenBase):
    """\
    Combining PortalTransforms with the document view generator.
    """

    def generateTitle(self, context):
        return u''

    def generateDescription(self, context):
        return u''

    def generateText(self, context):
        input = context.file()
        return self.convert(input)


class HTMLDocViewGen(PortalTransformDocViewGenBase):
    zope.interface.implements(IExposureFileDocViewGen)
    transform = 'safe_html'
    title = u'HTML annotator'
    description = u'This converts raw HTML files into a format suitable for ' \
                   'a Plone site.'


class RSTDocViewGen(PortalTransformDocViewGenBase):
    zope.interface.implements(IExposureFileDocViewGen)
    transform = 'rest_to_html'
    title = u'reStructuredText annotator'
    description = u'This converts raw RST files into a format suitable for ' \
                   'a Plone site.'
