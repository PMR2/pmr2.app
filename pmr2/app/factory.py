from cStringIO import StringIO

import zope.interface
import zope.component
from zope.location import Location, locate
from Products.CMFCore.utils import getToolByName
from Products.PortalTransforms.data import datastream

from pmr2.processor.cmeta import Cmeta
from pmr2.app.interfaces import *
import pmr2.app.util


def name_utility(obj, event):
    """\
    Writes the name of the utility when it is registered.  Used by
    subscriber.
    """

    locate(obj, None, event.object.name)

def named_factory(klass):
    """\
    Named Factory maker
    """

    class _factory(Location):
        zope.interface.implements(INamedUtilBase)
        def __init__(self):
            self.title = klass.title
            self.description = klass.description
        def __call__(self, context):
            # instantiate annotator and calls it.
            generator = klass(context)
            generator.__name__ = self.__name__
            generator()
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

    def __init__(self, context):
        super(ExposureFileAnnotatorBase, self).__init__(context)
        self.input = zope.component.getAdapter(
            self.context, IExposureSourceAdapter).file()

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
        if self.name not in context.views:
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
        return (
            ('text', self.convert(self.input).decode('utf8')),
        )

CellML2MathMLAnnotatorFactory = named_factory(CellML2MathMLAnnotator)


class RDFLibEFAnnotator(ExposureFileAnnotatorBase):

    def generate(self):
        metadata = Cmeta(StringIO(self.input))
        return (
            ('text', unicode(metadata.graph.serialize(format=self.format))),
        )


# DocView Generator
class DocViewGenBase(NamedUtilBase):
    """\
    Base utility class.
    """

    def __init__(self, context):
        super(DocViewGenBase, self).__init__(context)
        self.input = zope.component.getAdapter(
            self.context, IExposureDocViewGenSourceAdapter).file()

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
        PortalTransformGenBase, DocViewGenBase):
    """\
    Combining PortalTransforms with the document view generator.
    """

    def __init__(self, *a, **kw):
        super(PortalTransformDocViewGenBase, self).__init__(*a, **kw)

    def generateTitle(self):
        return u''

    def generateDescription(self):
        return u''

    def generateText(self):
        input = self.input
        return self.convert(input)


class HTMLDocViewGen(PortalTransformDocViewGenBase):
    zope.interface.implements(IDocViewGen)
    transform = 'safe_html'
    title = u'HTML annotator'
    description = u'This converts raw HTML files into a format suitable for ' \
                   'a Plone site.'

HTMLDocViewGenFactory = named_factory(HTMLDocViewGen)


class RSTDocViewGen(PortalTransformDocViewGenBase):
    zope.interface.implements(IDocViewGen)
    transform = 'rest_to_html'
    title = u'reStructuredText annotator'
    description = u'This converts raw RST files into a format suitable for ' \
                   'a Plone site.'

RSTDocViewGenFactory = named_factory(RSTDocViewGen)
