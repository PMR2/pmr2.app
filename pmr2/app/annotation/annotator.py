from cStringIO import StringIO

import zope.interface
import zope.component
from zope.annotation.interfaces import IAnnotations
from zope.annotation import factory

from Products.CMFCore.utils import getToolByName
from Products.PortalTransforms.data import datastream

from pmr2.app.exposure.interfaces import IExposureSourceAdapter
from pmr2.app.annotation.interfaces import *
from pmr2.app.factory import NamedUtilBase


class ExposureFileAnnotatorBase(NamedUtilBase):
    """
    The base annotator.
    """

    def __init__(self, context, request):
        # Lock the context - should never be changed.  Instantiate
        # another annotator class with another context if it is needed
        # on another one.
        self.__context = context
        self.__request = request

    @property
    def input(self):
        if not hasattr(self, '__input'):
            self.__input = zope.component.getAdapter(
                self.context, IExposureSourceAdapter).file()
        return self.__input

    @property
    def context(self):
        return self.__context

    @property
    def request(self):
        return self.__request

    @property
    def note(self):
        note = zope.component.getAdapter(self.context, name=self.name)
        # XXX not sure where or how the context is "pruned" of all its
        # parent nodes, sometimes...
        parent = note.__getattribute__('__parent__')
        if len(parent.getPhysicalPath()) == 1:
            # XXX this is a hack in getting the values "correct" in the 
            # way we need it to be.
            note.__setattr__('__parent__', note.__parent__)
        return note

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
                # XXX figure out how to gracefully handle schema errors
                # (such as missing values).
                setattr(note, a, v)
        except TypeError:
            raise TypeError('%s.generate failed to return a list of ' \
                            'tuple(key, value)' % self.__class__)
        except ValueError:
            raise ValueError('%s.generate returned invalid values (not ' \
                             'list of tuple(key, value)' % self.__class__)

    def __call__(self, data=None):
        """\
        Puts data into the note, depending on the nature of the note
        and this annotator.

        If the target note is not editable (i.e. one that does not
        implement IExposureFileEditableNote) all data will be generated.

        If the target note is editable (i.e. implements 
        IExposureFileEditableNote), the result is dependent on what this
        annotator implements.
        
        If the annotator only implements IExposureFileAnnotator, the 
        data parameter will provide the data which will be assigned to
        the note.  The method generate will not be called.
        
        If the annotator also implements IExposureFileEditableAnnotator,
        the data attribute provides the data, which is assigned, and
        the method generate will be called.
        """

        if not IExposureFileEditableNote.providedBy(self.note):
            data = self.generate()
            # XXX could verify all the data is generated based on what
            # is in self.for_interface.names()
            self._annotate(data)
            self._append_view()
            return

        # this must be editable notes.

        if data is not None:
            self._annotate(data)
            # XXX there may be cases a view is undefined.  Migration will
            # have to take note of this.
            self._append_view()
        else:
            # Q: Sould a warning be raised about that no data had been
            # provided and nothing was done?
            # A: Maybe, but this may be used by the form that starts the
            # process.  Could use a test case.
            pass

        if IExposureFilePostEditAnnotator.providedBy(self):
            # The subclass that implements generate must vadlidate any
            # data which may (or not) be annotated above.
            data = self.generate()
            self._annotate(data)


class PortalTransformGenBase(object):
    """\
    Utilizes Portal Transform to get content.
    """

    transform = None  # define this

    def convert(self, input):
        pt = getToolByName(self.context, 'portal_transforms')
        stream = datastream('pt_annotation')
        pt.convert(self.transform, input, stream)
        return stream.getData()


class PortalTransformAnnotatorBase(
        PortalTransformGenBase, ExposureFileAnnotatorBase):
    """\
    Combining PortalTransforms with the annotator.
    """


class RDFLibEFAnnotator(ExposureFileAnnotatorBase):
    """
    An example annotator.
    """

    def generate(self):
        from pmr2.rdf.graph import parseXML
        graph = parseXML(self.input)
        return (
            ('text', unicode(graph.serialize(format=self.format))),
        )
