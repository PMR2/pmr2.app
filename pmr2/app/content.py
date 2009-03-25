import zope.interface

from Products.Archetypes import atapi

from pmr2.app.interfaces import IExposureDocumentFactory
from pmr2.app.interfaces import IExposureMetadocFactory

from pmr2.app._content.root import PMR2

from pmr2.app._content.workspace import WorkspaceContainer
from pmr2.app._content.workspace import Workspace

from pmr2.app._content.sandbox import SandboxContainer
from pmr2.app._content.sandbox import Sandbox

from pmr2.app._content.exposure import ExposureContainer
from pmr2.app._content.exposure import Exposure
from pmr2.app._content.exposure import ExposureDocument
from pmr2.app._content.exposure import ExposureMathDocument
from pmr2.app._content.exposure import ExposureCmetaDocument
from pmr2.app._content.exposure import ExposureCodeDocument
from pmr2.app._content.exposure import ExposurePMR1Metadoc

from pmr2.app._content.support import PMR2Search


# type registration
atapi.registerType(ExposureContainer, 'pmr2.app')
atapi.registerType(Exposure, 'pmr2.app')
atapi.registerType(ExposureDocument, 'pmr2.app')
atapi.registerType(ExposureMathDocument, 'pmr2.app')
atapi.registerType(ExposureCmetaDocument, 'pmr2.app')
atapi.registerType(ExposureCodeDocument, 'pmr2.app')
atapi.registerType(ExposurePMR1Metadoc, 'pmr2.app')

def catalog_content(obj, event):
    obj.reindexObject()


class BaseExposureDocumentFactory(object):

    def __call__(self, filename):
        import pmr2.app.content  # sup?
        klass = getattr(pmr2.app.content, self.klass)
        # XXX identifier has to be normal str
        name = str(filename + self.suffix)
        obj = klass(oid=name)
        # XXX unclean
        if hasattr(self, 'transform'):
            obj.transform = self.transform
        # XXX filename conversion to unicode
        obj.origin = unicode(filename)
        return obj


# ExposureDocumentFactory is the default type, it does nothing for now.

class ExposurePMR1DocumentFactory(BaseExposureDocumentFactory):

    zope.interface.implements(IExposureDocumentFactory)

    klass = u'ExposureDocument'
    description = u'PMR1 CellML Docbook Page'
    suffix = u'.pmr1.html'
    transform = u'pmr2_processor_legacy_tmpdoc2html'


class ExposureMathDocumentFactory(BaseExposureDocumentFactory):

    zope.interface.implements(IExposureDocumentFactory)

    klass = u'ExposureMathDocument'
    description = u'PMR1 MathML Page'
    suffix = u'.mathml.html'
    transform = u'pmr2_processor_legacy_cellml2html_mathml'


class ExposureCmetaDocumentFactory(BaseExposureDocumentFactory):

    zope.interface.implements(IExposureDocumentFactory)

    klass = u'ExposureCmetaDocument'
    description = u'CellML Metadata Page'
    suffix = u'.pmr2.cmeta'
    transform = u'pmr2_cellml_metadata'  # this needed?


class ExposureCodeDocumentFactory(BaseExposureDocumentFactory):

    zope.interface.implements(IExposureDocumentFactory)

    klass = u'ExposureCodeDocument'
    description = u'CellML Code Generation Page'
    suffix = u'.code.html'
    transform = u'pmr2_processor_cellmlapi_cellml2c'


class ExposurePMR1MetadocFactory(BaseExposureDocumentFactory):

    zope.interface.implements(IExposureMetadocFactory)

    klass = u'ExposurePMR1Metadoc'
    description = u'PMR1 Style Exposure'
    suffix = u'.index.html'
