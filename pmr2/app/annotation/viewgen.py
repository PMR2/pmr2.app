from cStringIO import StringIO

import zope.interface
import zope.component
from elementtree import HTMLTreeBuilder

from pmr2.app.interfaces import *
from pmr2.app.factory import NamedUtilBase, named_factory

# XXX while this particular class should be imported from there, maybe
# it shouldbe be defined there.
from pmr2.app.annotation.annotator import PortalTransformGenBase


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
