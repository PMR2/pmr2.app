from cStringIO import StringIO

import zope.interface
import zope.component
from zope.annotation.interfaces import IAnnotations
from zope.annotation import factory

from Products.CMFCore.utils import getToolByName
from Products.PortalTransforms.data import datastream

from pmr2.processor.cmeta import Cmeta
from pmr2.app.interfaces import *
from pmr2.app.annotation.interfaces import *
from pmr2.app.factory import NamedUtilBase
import pmr2.app.util


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
        # XXX reimplement using plain rdflib.
        metadata = Cmeta(StringIO(self.input))
        return (
            ('text', unicode(metadata.graph.serialize(format=self.format))),
        )
