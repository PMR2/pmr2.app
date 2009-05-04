import os.path
from cStringIO import StringIO

from zope import interface
from zope.schema import fieldproperty

from AccessControl import ClassSecurityInfo
from Acquisition import aq_parent, aq_inner
from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin
from Products.ATContentTypes.content.folder import ATFolder, ATBTreeFolder
from Products.ATContentTypes.content.document import ATDocument
from Products.Archetypes.atapi import BaseContent
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.permissions import View, ModifyPortalContent
from Products.PortalTransforms.data import datastream

import pmr2.mercurial.interfaces

from pmr2.processor.cmeta import Cmeta

from pmr2.app.interfaces import *
from pmr2.app.mixin import TraversalCatchAll
import pmr2.app.util


class ExposureContainer(ATBTreeFolder):
    """\
    Container for exposures in PMR2.
    """

    interface.implements(IExposureContainer)
    security = ClassSecurityInfo()

    def __init__(self, oid='exposure', **kwargs):
        super(ExposureContainer, self).__init__(oid, **kwargs)

    security.declarePrivate('get_path')
    def get_path(self):
        # XXX quickie code
        #"""See IWorkspaceContainer"""

        p = aq_parent(aq_inner(self)).repo_root
        if not p:
            return None
        # XXX magic string
        return os.path.join(p, 'workspace')


class ExposureContentIndexBase(object):
    """\
    Provides default values for the indexes we use for plone catalog.

    Also ZCatalog compatibility, see below.
    """

    interface.implements(IExposureContentIndex)

    def get_authors_family_index(self):
        return ()

    def get_citation_title_index(self):
        return ()

    def get_curation_index(self):
        return ()

    def get_keywords_index(self):
        return ()

    def get_exposure_workspace_index(self):
        return ()

    def get_exposure_root_title(self):
        return ''

    def get_exposure_root_path(self):
        return ''

    def get_exposure_root_id(self):
        return ''

    # ZCatalog compatibility hack to make mybrains objects returned from
    # a catalog search to contain values we want indexed.  The method,
    # Products.ZCatalog.Catalog.recordify, does not support index_attr, 
    # so the # above methods will not be called and the index name 
    # listed in the catalog.xml we defined in our default profile will 
    # be used as the attribute instead, which will not exist unless they
    # are defined in the objects.  So we have to do the deed here.

    @property
    def pmr2_authors_family_name(self):
        return self.get_authors_family_index()

    @property
    def pmr2_citation_title(self):
        return self.get_citation_title_index()

    @property
    def pmr2_curation(self):
        return self.get_curation_index()

    @property
    def pmr2_keyword(self):
        return self.get_keywords_index()

    @property
    def pmr2_exposure_workspace(self):
        return self.get_exposure_workspace_index()

    @property
    def pmr2_exposure_root_title(self):
        return self.get_exposure_root_title()

    @property
    def pmr2_exposure_root_path(self):
        return self.get_exposure_root_path()

    @property
    def pmr2_exposure_root_id(self):
        return self.get_exposure_root_id()


class Exposure(ATFolder, TraversalCatchAll, ExposureContentIndexBase):
    """\
    PMR Exposure object is used to encapsulate a single version of any
    given workspace and will allow more clear presentation to users of
    the system.

    This is implemented as a folder to allow inclusion of different 
    types of data that may be generated as part of the exposure process,
    such as data plots for graphs, graphical representation of metadata
    or the generated diagrams of models, or even other types of data.

    Naturally, specific types of extended exposure data will need to
    have classes defined for them.
    """

    interface.implements(IExposure)
    security = ClassSecurityInfo()
    # XXX the get_ methods are similar to IWorkspace.
    # best to define a common interface.

    workspace = fieldproperty.FieldProperty(IExposure['workspace'])
    commit_id = fieldproperty.FieldProperty(IExposure['commit_id'])
    curation = fieldproperty.FieldProperty(IExposure['curation'])

    def __before_publishing_traverse__(self, ob, request):
        TraversalCatchAll.__before_publishing_traverse__(self, ob, request)
        ATFolder.__before_publishing_traverse__(self, ob, request)

    security.declareProtected(View, 'get_authors_family_index')
    def get_authors_family_index(self):
        # XXX stub, do not know if we should get values from children
        # or how should we implement this.
        return ()

    security.declareProtected(View, 'get_citation_title_index')
    def get_citation_title_index(self):
        # XXX stub, see get_authors_family_index
        return ()

    security.declareProtected(View, 'get_curation_index')
    def get_curation_index(self):
        # FIXME this should really be sharing code with the converter 
        # class
        result = []
        if not self.curation:
            return result
        result.extend(self.curation.keys())
        for k, v in self.curation.iteritems():
            for i in v:
                result.append('%s:%s' % (k, i))
                result.sort()
        return result

    security.declareProtected(View, 'get_keywords_index')
    def get_keywords_index(self):
        # XXX stub, see get_authors_family_index
        return ()

    security.declareProtected(View, 'get_exposure_workspace_index')
    def get_exposure_workspace_index(self):
        return self.workspace

    security.declareProtected(View, 'get_exposure_root_title')
    def get_exposure_root_title(self):
        return self.Title()

    security.declareProtected(View, 'get_exposure_root_path')
    def get_exposure_root_path(self):
        return self.absolute_url_path()

    security.declareProtected(View, 'get_exposure_root_id')
    def get_exposure_root_id(self):
        return self.id


class ExposureDocument(ATDocument, ExposureContentIndexBase):  #, TraversalCatchAll):
    """\
    Documentation for an exposure.
    """

    interface.implements(IExposureDocument)
    security = ClassSecurityInfo()

    origin = fieldproperty.FieldProperty(IExposureDocument['origin'])
    transform = fieldproperty.FieldProperty(IExposureDocument['transform'])
    metadoc = fieldproperty.FieldProperty(IExposureDocument['metadoc'])

    def _convert(self):
        # this grabs contents of file from workspace (hg)

        storage = zope.component.queryMultiAdapter(
            (self,),
            name='PMR2ExposureDocStorageAdapter',
        )
        input = storage.file

        pt = getToolByName(self, 'portal_transforms')
        stream = datastream('processor')
        pt.convert(self.transform, input, stream)
        return stream.getData()

    security.declareProtected(ModifyPortalContent, 'generate_content')
    def generate_content(self):
        self.setTitle(u'Documentation')
        self.setDescription(u'Generated from %s' % self.origin)
        self.setContentType('text/html')
        self.setText(self._convert())

    def _getmetadoc(self):
        """
        Quick way to access metadoc object, assuming nothing is broken.
        """
        # XXX adapter to deal with this and methods below
        parent = aq_parent(aq_inner(self))
        if parent is None:
            # XXX catalog calls aq_base to untangle object, so we need
            # another way to get to the parent object (to get it into
            # the catalog for quick access in searches.
            return None
        if self.metadoc and self.metadoc in parent:
            try:
                metadoc = parent[self.metadoc]
            except:
                return None
            return metadoc

    security.declareProtected(View, 'get_subdocument_structure')
    def get_subdocument_structure(self):
        metadoc = self._getmetadoc()
        if metadoc:
            docstruct = metadoc.get_subdocument_structure()
            return docstruct

    security.declareProtected(View, 'get_exposure_root_title')
    def get_exposure_root_title(self):
        metadoc = self._getmetadoc()
        if metadoc:
            return metadoc.Title()
        return self.Title()

    security.declareProtected(View, 'get_exposure_root_path')
    def get_exposure_root_path(self):
        metadoc = self._getmetadoc()
        if metadoc:
            return metadoc.absolute_url_path()
        return self.absolute_url_path()

    security.declareProtected(View, 'get_exposure_root_id')
    def get_exposure_root_id(self):
        metadoc = self._getmetadoc()
        if metadoc:
            return metadoc.id
        return self.id


class ExposureMetadoc(
    BrowserDefaultMixin, 
    BaseContent, 
    ExposureContentIndexBase,
):

    interface.implements(IExposureMetadoc)
    security = ClassSecurityInfo()

    origin = fieldproperty.FieldProperty(IExposureMetadoc['origin'])
    factories = fieldproperty.FieldProperty(IExposureMetadoc['factories'])

    security.declareProtected(View, 'get_subdocument_structure')
    def get_subdocument_structure(self):
        result = {}
        subdocs = []
        # XXX following is naive code
        parent = aq_parent(aq_inner(self))
        for id_ in self.subdocument:
            if id_ not in parent:
                # Something wrong.
                continue
            subdocs.append({
                'id': id_,
                'label': parent[id_].title,
                'href': parent[id_].absolute_url(),
            })
        result['id'] = self.id
        result['title'] = self.title
        result['root_url'] = self.absolute_url()
        result['subdocs'] = subdocs
        return result

    security.declareProtected(View, 'get_exposure_root_title')
    def get_exposure_root_title(self):
        return self.Title()

    security.declareProtected(View, 'get_exposure_root_path')
    def get_exposure_root_path(self):
        return self.absolute_url_path()

    security.declareProtected(View, 'get_exposure_root_id')
    def get_exposure_root_id(self):
        return self.id


class ExposureMathDocument(ExposureDocument):
    """\
    Documentation for an exposure for use with MathML.
    """

    interface.implements(IExposureMathDocument)
    #origin = fieldproperty.FieldProperty(IExposureMathDocument['origin'])
    #transform = fieldproperty.FieldProperty(IExposureMathDocument['transform'])
    mathml = fieldproperty.FieldProperty(IExposureMathDocument['mathml'])
    security = ClassSecurityInfo()

    security.declareProtected(ModifyPortalContent, 'generate_content')
    def generate_content(self):
        self.setTitle(u'Mathematics')
        self.setDescription(u'Generated from %s' % self.origin)
        self.setContentType('text/html')
        self.mathml = self._convert().decode('utf-8')
        self.setText(u'')
        # disabled due to XSS flaw.
        #self.setText(u'<object style="width: 100%%;height:25em;" data="%s/@@view_mathml"></object>' % self.absolute_url())


class ExposureCmetaDocument(ExposureDocument):
    """\
    Contains a rendering of the CellML Metadata.
    """
    # XXX this class should be part of the metdata, and registered into
    # some sort of database that will automatically load this up into
    # one of the valid document types that can be added.

    interface.implements(IExposureCmetaDocument)
    security = ClassSecurityInfo()

    metadata = fieldproperty.FieldProperty(IExposureCmetaDocument['metadata'])
    citation_authors = fieldproperty.FieldProperty(IExposureCmetaDocument['citation_authors'])
    citation_title = fieldproperty.FieldProperty(IExposureCmetaDocument['citation_title'])
    citation_bibliographicCitation = fieldproperty.FieldProperty(IExposureCmetaDocument['citation_bibliographicCitation'])
    citation_id = fieldproperty.FieldProperty(IExposureCmetaDocument['citation_id'])
    keywords = fieldproperty.FieldProperty(IExposureCmetaDocument['keywords'])

    security.declareProtected(ModifyPortalContent, 'generate_content')
    def generate_content(self):
        self.setTitle(u'Model Metadata')
        self.setDescription(u'Generated from %s' % self.origin)
        self.setContentType('text/html')

        storage = zope.component.queryMultiAdapter(
            (self,),
            name='PMR2ExposureDocStorageAdapter',
        )
        input = storage.file

        metadata = Cmeta(StringIO(input))
        ids = metadata.get_cmetaid()
        if not ids:
            return

        citation = metadata.get_citation(ids[0])
        if not citation:
            return

        self.citation_id = citation[0]['citation_id']
        # more than just journal
        self.citation_bibliographicCitation = citation[0]['journal']
        self.citation_title = citation[0]['title']

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
            
        self.citation_authors = authors
        self.keywords = metadata.get_keywords()

    security.declareProtected(View, 'citation_authors_string')
    def citation_authors_string(self):
        if not self.citation_authors:
            return u''
        middle = u'</li>\n<li>'.join(
            ['%s, %s %s' % i for i in self.citation_authors])
        return u'<ul>\n<li>%s</li>\n</ul>' % middle

    security.declareProtected(View, 'citation_id_html')
    def citation_id_html(self):
        if not self.citation_id:
            return u''
        http = pmr2.app.util.infouri2http(self.citation_id)
        if http:
            return '<a href="%s">%s</a>' % (http, self.citation_id)
        return self.citation_id

    security.declareProtected(View, 'get_authors_family_index')
    def get_authors_family_index(self):
        if self.citation_authors:
            return [pmr2.app.util.normal_kw(i[0]) 
                    for i in self.citation_authors]
        else:
            return []

    security.declareProtected(View, 'get_citation_title_index')
    def get_citation_title_index(self):
        if self.citation_title:
            return pmr2.app.util.normal_kw(self.citation_title)

    security.declareProtected(View, 'get_keywords_index')
    def get_keywords_index(self):
        if self.keywords:
            # XXX magical replace
            results = [pmr2.app.util.normal_kw(i[1]) for i in self.keywords]
            results.sort()
            return results
        else:
            return []


class ExposureCodeDocument(ExposureDocument):
    """\
    Wrapper to display code.
    """

    interface.implements(IExposureCodeDocument)
    security = ClassSecurityInfo()

    raw_code = fieldproperty.FieldProperty(IExposureCodeDocument['raw_code'])

    security.declareProtected(ModifyPortalContent, 'generate_content')
    def generate_content(self):
        self.setTitle(u'Procedural Code')
        self.setDescription(u'Generated from %s' % self.origin)
        self.setContentType('text/html')
        # XXX magic encoding
        self.raw_code = unicode(self._convert(), encoding='latin1')
        # could do similar thing as MathML View to save space, but not
        # worth doing for now due to time.
        self.setText('<pre><code>%s</code></pre>' % self.raw_code)


class ExposurePMR1Metadoc(ExposureMetadoc):
    """\
    Exposure meta document that will generate all related PMR1 views
    for an exposure.
    """

    security = ClassSecurityInfo()

    security.declareProtected(ModifyPortalContent, 'generate_content')
    def generate_content(self):
        parent = aq_parent(aq_inner(self))
        subdoc = []
        self.title = 'Overview of %s' % self.origin
        for i in self.factories:
            factory = zope.component.queryUtility(IExposureDocumentFactory, i)
            obj = factory(self.origin)
            parent[obj.id] = obj
            obj = parent[obj.id]
            obj.generate_content()

            # give object reference to this metadoc
            obj.metadoc = unicode(self.id)

            obj.notifyWorkflowCreated()
            obj.reindexObject()
            subdoc.append(obj.id)

            # XXX
            if i == u'ExposureCmetaDocumentFactory' and obj.citation_title:
                self.title = obj.citation_title

        self.subdocument = subdoc

    # XXX use adapter adapt this class to the required classes to get
    # the data for the next two methods.
    security.declareProtected(View, 'get_documentation')
    def get_documentation(self):
        # XXX use catalog?
        lookup = dict(zip(self.factories, self.subdocument))
        id = lookup[u'ExposurePMR1DocumentFactory']
        return self.aq_parent[id].getText()

    security.declareProtected(View, 'get_pmr1_curation')
    def get_pmr1_curation(self):
        pairs = (
            ('pmr_curation_star', u'Curation Status:'),
            ('pmr_pcenv_star', u'PCEnv:'),
            ('pmr_jsim_star', u'JSim:'),
            ('pmr_cor_star', u'COR:'),
        )
        curation = aq_parent(self).curation or {}
        result = []
        for key, label in pairs:
            # first item or character
            stars = key in curation and curation[key][0] or u'0'
            result.append({
                'label': label,
                'stars': stars,
            })
        return result
