from cStringIO import StringIO

from zope.schema import fieldproperty
from zope.location import Location, locate
import zope.interface
import zope.component
from elementtree import HTMLTreeBuilder

from pmr2.app.interfaces import *
from pmr2.app.exposure.interfaces import *
from pmr2.app.exposure.browser.interfaces import *
from pmr2.app.exposure.adapter import ExposureSourceAdapter
from pmr2.app.factory import NamedUtilBase, named_factory

from pmr2.app.annotation.interfaces import *

# XXX while this particular class should be imported from there, maybe
# it shouldbe be defined there.
from pmr2.app.annotation.annotator import PortalTransformGenBase


# DocView Generator
class DocViewGenBase(NamedUtilBase):
    """\
    Base utility class.
    """

    mimetype = 'text/html'

    def __init__(self, context, input=None):
        super(DocViewGenBase, self).__init__(context)
        self.input = input
        if input is None:
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
        context.setText(self.generateText(), mimetype=self.mimetype)
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


# Supporting adapters

class ExposureFileNoteSourceAdapter(ExposureSourceAdapter):

    def __init__(self, context):
        self.context = context.__parent__
        # Since an annotation note should have a parent that provides
        # IExposureObject, this should pass
        assert IExposureObject.providedBy(self.context)

class ExposureDocViewGenSourceAdapter(ExposureSourceAdapter):
    """\
    To make acquiring the contents of the file easier, we reuse the
    ExposureSourceAdapter with a tweek to use the docview_gensource
    attribute of the ExposureObject.
    """

    zope.interface.implements(IExposureDocViewGenSourceAdapter)

    def source(self):
        exposure, workspace, path = ExposureSourceAdapter.source(self)
        # object could provide a source path
        if hasattr(self.context, 'docview_gensource') and \
                self.context.docview_gensource:
            path = self.context.docview_gensource
        return exposure, workspace, path


class ExposureDocViewGenFormSourceAdapter(ExposureFileNoteSourceAdapter,
        ExposureDocViewGenSourceAdapter):
    """\
    Data source for the class below.
    """


class ExposureDocViewGenForm(Location):

    zope.interface.implements(IExposureDocViewGenForm)
    docview_gensource = fieldproperty.FieldProperty(IExposureDocViewGenForm['docview_gensource'])
    docview_generator = fieldproperty.FieldProperty(IExposureDocViewGenForm['docview_generator'])

    def __init__(self, context):
        # must locate itself into context the very first thing, as the
        # vocabulary uses source adapter registered above.
        locate(self, context, '')
        self.docview_gensource = context.docview_gensource
        self.docview_generator = context.docview_generator
