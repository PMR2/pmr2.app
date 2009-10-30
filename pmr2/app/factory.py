from cStringIO import StringIO

import zope.interface
import zope.component
from zope.location import Location, locate
from Products.CMFCore.utils import getToolByName
from Products.PortalTransforms.data import datastream

from pmr2.processor.cmeta import Cmeta
from pmr2.app.interfaces import IExposureFileAnnotator
from pmr2.app.interfaces import IExposureFileViewUtility
from pmr2.app.interfaces import IExposureFileViewAssignmentForm


def name_utility(obj, event):
    # writes the name of the annotator is registered under into the 
    # annotator
    locate(obj, None, event.object.name)


class ExposureFileAnnotatorBase(Location):

    view = None

    def generate(self):
        raise NotImplementedError

    def __call__(self, context):
        # assert context implements IExposureFile?
        self.context = context
        # let subclasses know not to muck with this
        self.__annotation = zope.component.queryAdapter(
            context, name=self.__name__)
        # shouldn't really have to muck around with this either
        self._input = self.context.file()
        # XXX query for the method?
        self.generate()
        # we are done, let the view to be used be noted
        if self.view is not None and self.view not in context.views:
            v = context.views
            v.append(self.view)
            context.views = v

    @property
    def input(self):
        if not hasattr(self, '_input'):
            self._input = self.context.file()
        return self._input

    @property
    def annotation(self):
        return self.__annotation


class PortalTransformAnnotatorBase(ExposureFileAnnotatorBase):
    """\
    Utilizes Portal Transform to get content.  By default it tries to
    turn files into HTML.
    """

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


class RDFTurtleAnnotator(ExposureFileAnnotatorBase):
    zope.interface.implements(IExposureFileAnnotator)
    title = u'RDF Turtle'
    description = u'This extracts and converts a CellML with RDF (or an RDF ' \
                   'file) into Turtle format for display.'

    def generate(self):
        metadata = Cmeta(StringIO(self.input))
        self.annotation.text = unicode(
            metadata.graph.serialize(format='turtle'))


class RDFn3Annotator(ExposureFileAnnotatorBase):
    zope.interface.implements(IExposureFileAnnotator)
    title = u'RDF n-Triple'
    description = u'This extracts and converts a CellML with RDF (or an RDF ' \
                   'file) into n-triple format for display.'

    def generate(self):
        metadata = Cmeta(StringIO(self.input))
        self.annotation.text = unicode(
            metadata.graph.serialize(format='n3'))


class RDFxmlAnnotator(ExposureFileAnnotatorBase):
    zope.interface.implements(IExposureFileAnnotator)
    title = u'RDF xml'
    description = u'This extracts and converts a CellML with RDF (or an RDF ' \
                   'file) into xml format for display.'

    def generate(self):
        metadata = Cmeta(StringIO(self.input))
        self.annotation.text = unicode(
            metadata.graph.serialize(format='xml'))


class ExposureFileViewUtility(Location):
    """\
    This utility is for the views and not the context.  Instances of
    this should be registered with the same name as the view it is meant
    to be for.
    """

    zope.interface.implements(IExposureFileViewUtility)
    # view is the name of this thing
    # annotators is defined in subclass

    @property
    def annotator(self):
        if not hasattr(self, '__annotator'):
            self.__annotator = zope.component.getUtility(
                IExposureFileAnnotator, name=self.__name__)
        return self.__annotator

    @property
    def title(self):
        return self.annotator.title

    @property
    def description(self):
        return self.annotator.description

    def __read(self, context):
        """\
        Parse the context into an object with the required fields.
        """

        result = zope.component.queryAdapter(context, name=self.__name__)
        return result

    def __write(self, context):
        # the adapters used should be assigned by the annotator classes.
        self.annotator(context)
        # as this utility is registered with the same name as the view
        # that this reader/writer is for, append it the context to
        # mark the view as generated.
        views = context.views or []  # need a list
        views.append(self.__name__)
        # write: to generate this view, this annonator was used
        context.views = views

    def __call__(self, view):
        context = view.context
        if IExposureFileViewAssignmentForm.providedBy(view):
            # the form view writes data.
            self.__write(context)
        else:
            return self.__read(context)
