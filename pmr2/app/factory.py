from cStringIO import StringIO

import zope.interface

from pmr2.processor.cmeta import Cmeta
from pmr2.app.interfaces import IExposureFileAnnotator

class ExposureFileAnnotatorBase(object):

    def generate(self):
        raise NotImplementedError

    def __call__(self, context):
        name = self.__name__
        # assert context implements IExposureFile?
        self.context = context
        self.annotation = zope.component.queryAdapter(context, name=name)
        self.generate()
        # we are done, let the adapters be added
        if name not in context.adapters:
            a = context.adapters
            a.append(name)
            context.adapters = a


class RDFTurtleAnnotator(ExposureFileAnnotatorBase):
    zope.interface.implements(IExposureFileAnnotator)

    __name__ = 'RDFTurtle'  # XXX this should be automatically derived.

    def generate(self):
        input = self.context.file()
        metadata = Cmeta(StringIO(input))
        self.annotation.text = unicode(
            metadata.graph.serialize(format='turtle'))
