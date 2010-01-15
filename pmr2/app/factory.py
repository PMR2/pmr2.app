from cStringIO import StringIO

import zope.interface
import zope.component
from zope.location import Location, locate
from Products.CMFCore.utils import getToolByName
from Products.PortalTransforms.data import datastream
from elementtree import HTMLTreeBuilder

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
            self.label = klass.label
            self.description = klass.description
        def __call__(self, context):
            # returns an instantiated factory with a context
            factory = klass(context)
            factory.__name__ = self.__name__
            return factory
    # create/return instance of the factory that instantiates the 
    # classes below.
    return _factory()


class NamedUtilBase(Location):
    """\
    Class that allows a utility to be named.
    """

    zope.interface.implements(INamedUtilBase)
    title = None
    label = None
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


class ExposureFileEditableAnnotatorBase(NamedUtilBase):
    """
    An editable annotator.
    """

    def __init__(self, context):
        # Lock the context - should never be changed.  Instantiate
        # another annotator class with another context if it is needed
        # on another one.
        self.__context = context

    @property
    def context(self):
        return self.__context

    @property
    def note(self):
        return zope.component.getAdapter(self.context, name=self.name)

    def generate(self):
        raise NotImplementedError

    def _append_view(self):
        # Append the name of this view since this must be registered 
        # with the same name as the annotator class.
        if self.name not in self.context.views:
            # going to be defensive here as we need to append to a list
            views = self.context.views or []  
            views.append(self.name)
            # write: to generate this view, this annonator was used
            self.context.views = views

    def _annotate(self, data):
        note = self.note
        try:
            for a, v in data:
                # XXX should validate field/value by schema somehow
                setattr(note, a, v)
        except TypeError:
            raise TypeError('%s.generate failed to return a list of ' \
                            'tuple(key, value)' % self.__class__)
        except ValueError:
            raise ValueError('%s.generate returned invalid values (not ' \
                             'list of tuple(key, value)' % self.__class__)

    def __call__(self, data=None):
        """
        If it's an editable note data is ignored, however in the future 
        there may be a need for a mixture of generated and user
        specified data.
        """

        if not IExposureFileEditableNote.providedBy(self.note):
            data = self.generate()
        if data:
            self._annotate(data)
            self._append_view()
        else:
            # XXX should a warning be raised about that no data had 
            # been provided and nothing was done?
            pass


class ExposureFileAnnotatorBase(ExposureFileEditableAnnotatorBase):
    """\
    The original standard annotator, defined to be uneditable thus 
    require the source file.
    """

    def __init__(self, context):
        super(ExposureFileAnnotatorBase, self).__init__(context)
        self.input = zope.component.getAdapter(
            self.context, IExposureSourceAdapter).file()


class PortalTransformAnnotatorBase(
        PortalTransformGenBase, ExposureFileAnnotatorBase):
    """\
    Combining PortalTransforms with the annotator.
    """


class CellML2MathMLAnnotator(PortalTransformAnnotatorBase):
    zope.interface.implements(IExposureFileAnnotator)
    transform = 'pmr2_processor_legacy_cellml2html_mathml'
    title = u'Basic MathML'
    label = u'Mathematics'
    description = u''

    def generate(self):
        return (
            ('text', self.convert(self.input).decode('utf8')),
        )

CellML2MathMLAnnotatorFactory = named_factory(CellML2MathMLAnnotator)


class CellML2CAnnotator(PortalTransformAnnotatorBase):
    zope.interface.implements(IExposureFileAnnotator)
    transform = 'pmr2_processor_cellmlapi_cellml2c'
    title = u'CellML C Code Generation'
    label = u'Procedural C Code'
    description = u''

    def generate(self):
        return (
            ('text', self.convert(self.input).decode('utf8')),
        )

CellML2CAnnotatorFactory = named_factory(CellML2CAnnotator)


class RDFLibEFAnnotator(ExposureFileAnnotatorBase):

    def generate(self):
        metadata = Cmeta(StringIO(self.input))
        return (
            ('text', unicode(metadata.graph.serialize(format=self.format))),
        )


class OpenCellSessionAnnotator(ExposureFileEditableAnnotatorBase):
    zope.interface.implements(IExposureFileAnnotator)
    title = u'OpenCell Session Link'
    label = u'OpenCell Session'

    def generate(self):
        return ()

OpenCellSessionAnnotatorFactory = named_factory(OpenCellSessionAnnotator)


class CmetaAnnotator(ExposureFileAnnotatorBase):
    zope.interface.implements(IExposureFileAnnotator)
    title = u'Basic CellML Metadata'
    label = u'Model Metadata'

    def generate(self):
        input = self.input
        result = {}
        metadata = Cmeta(StringIO(input))
        ids = metadata.get_cmetaid()
        if not ids:
            # got no metadata.
            return ()

        citation = metadata.get_citation(ids[0])
        if not citation:
            # no citation, everyone go home
            return ()

        result['citation_id'] = citation[0]['citation_id']
        # more than just journal
        result['citation_bibliographicCitation'] = citation[0]['journal']
        result['citation_title'] = citation[0]['title']

        # XXX ad-hoc sanity checking
        issued = citation[0]['issued']
        if pmr2.app.util.simple_valid_date(issued):
            result['citation_issued'] = issued
        else:
            result['citation_issued'] = u''

        authors = []
        for c in citation[0]['creator']:
            family = c['family']
            given = c['given']
            if c['other']:
                other = ' '.join(c['other'])
            else:
                other = ''
            fn = (family, given, other)
            authors.append(fn)
            
        result['citation_authors'] = authors
        result['keywords'] = metadata.get_keywords()

        dcvc = metadata.get_dc_vcard_info(node='')
        if dcvc:
            # using only first one
            info = dcvc[0]
            result['model_title'] = info['title']
            result['model_author'] = '%s %s' % (info['given'], info['family'])
            result['model_author_org'] = \
                '%s, %s' % (info['orgunit'], info['orgname']) 
        # annotators are expected to return a list of tuples.
        return result.items()

CmetaAnnotatorFactory = named_factory(CmetaAnnotator)


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
        # don't generate title
        return self.context.Title()

    def generateDescription(self):
        # don't generate description
        return self.context.Description()

    def generateText(self):
        input = self.input
        return self.convert(input)


class HTMLDocViewGen(PortalTransformDocViewGenBase):
    zope.interface.implements(IDocViewGen)
    transform = 'safe_html'
    title = u'HTML annotator'
    description = u'This converts raw HTML files into a format suitable for ' \
                   'a Plone site.'

    def generateTitle(self):
        try:
            tree = HTMLTreeBuilder.parse(StringIO(self.input))
            return tree.findtext("head/title")
        except:
            pass
        return self.context.Title()

HTMLDocViewGenFactory = named_factory(HTMLDocViewGen)


class RSTDocViewGen(PortalTransformDocViewGenBase):
    zope.interface.implements(IDocViewGen)
    transform = 'rest_to_html'
    title = u'reStructuredText annotator'
    description = u'This converts raw RST files into a format suitable for ' \
                   'a Plone site.'

RSTDocViewGenFactory = named_factory(RSTDocViewGen)
