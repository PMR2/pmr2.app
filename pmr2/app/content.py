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
from pmr2.app._content.exposure import ExposureFile
from pmr2.app._content.exposure import ExposureFolder

# legacy Exposure types
from pmr2.app._content.exposure import ExposureDocument
from pmr2.app._content.exposure import ExposureMathDocument
from pmr2.app._content.exposure import ExposureCmetaDocument
from pmr2.app._content.exposure import ExposureCodeDocument
from pmr2.app._content.exposure import ExposurePMR1Metadoc

from pmr2.app._content.support import PMR2Search


# type registration
atapi.registerType(ExposureContainer, 'pmr2.app')
atapi.registerType(Exposure, 'pmr2.app')
atapi.registerType(ExposureFile, 'pmr2.app')
atapi.registerType(ExposureFolder, 'pmr2.app')

atapi.registerType(ExposureDocument, 'pmr2.app')
atapi.registerType(ExposureMathDocument, 'pmr2.app')
atapi.registerType(ExposureCmetaDocument, 'pmr2.app')
atapi.registerType(ExposureCodeDocument, 'pmr2.app')
atapi.registerType(ExposurePMR1Metadoc, 'pmr2.app')

def catalog_content(obj, event):
    obj.reindexObject()


class BaseDocumentFactory(object):
    """\
    The base document factory for exposure.
    """

    def __call__(self, filename):
        name = str(filename + self.suffix)
        obj = self.klass(oid=name)
        # XXX filename conversion to unicode
        obj.origin = unicode(filename)
        return obj


class BaseExposureDocumentFactory(BaseDocumentFactory):
    """\
    The base ExposureDocument factory.
    """

    def __call__(self, filename):
        obj = super(BaseExposureDocumentFactory, self).__call__(filename)
        obj.transform = self.transform
        return obj


class BaseExposureMetadocFactory(BaseDocumentFactory):
    """\
    The base ExposureMetadoc factory.
    """

    def __call__(self, filename):
        obj = super(BaseExposureMetadocFactory, self).__call__(filename)
        obj.factories = self.factories
        return obj


class ExposurePMR1DocumentFactory(BaseExposureDocumentFactory):

    zope.interface.implements(IExposureDocumentFactory)

    klass = ExposureDocument
    description = u'PMR1 CellML Docbook Page'
    suffix = u'.pmr1.html'
    transform = u'pmr2_processor_legacy_tmpdoc2html'


class ExposureMathDocumentFactory(BaseExposureDocumentFactory):

    zope.interface.implements(IExposureDocumentFactory)

    klass = ExposureMathDocument
    description = u'PMR1 MathML Page'
    suffix = u'.mathml.html'
    transform = u'pmr2_processor_legacy_cellml2html_mathml'


class ExposureCmetaDocumentFactory(BaseExposureDocumentFactory):

    zope.interface.implements(IExposureDocumentFactory)

    klass = ExposureCmetaDocument
    description = u'CellML Metadata Page'
    suffix = u'.pmr2.cmeta'
    transform = u'pmr2_cellml_metadata'  # this needed?


class ExposureCodeDocumentFactory(BaseExposureDocumentFactory):

    zope.interface.implements(IExposureDocumentFactory)

    klass = ExposureCodeDocument
    description = u'CellML Code Generation Page'
    suffix = u'.code.html'
    transform = u'pmr2_processor_cellmlapi_cellml2c'


class ExposurePMR1MetadocFactory(BaseExposureMetadocFactory):

    zope.interface.implements(IExposureMetadocFactory)

    klass = ExposurePMR1Metadoc
    description = u'PMR1 Style Exposure'
    suffix = u'.index.html'
    factories = [
        u'ExposurePMR1DocumentFactory',
        u'ExposureMathDocumentFactory',
        u'ExposureCmetaDocumentFactory',
        u'ExposureCodeDocumentFactory',
    ]
