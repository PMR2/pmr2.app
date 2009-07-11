import re
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

    def pmr2_authors_family_name(self):
        return self.get_authors_family_index()

    def pmr2_citation_title(self):
        return self.get_citation_title_index()

    def pmr2_curation(self):
        return self.get_curation_index()

    def pmr2_keyword(self):
        return self.get_keywords_index()

    def pmr2_exposure_workspace(self):
        return self.get_exposure_workspace_index()

    def pmr2_exposure_root_title(self):
        return self.get_exposure_root_title()

    def pmr2_exposure_root_path(self):
        return self.get_exposure_root_path()

    def pmr2_exposure_root_id(self):
        return self.get_exposure_root_id()

    # XXX PMR1 display mode compatibility hack
    def pmr1_citation_authors(self):
        return ''

    def pmr1_citation_title(self):
        return ''

    def pmr1_citation_authors_sortable(self):
        s = self.pmr1_citation_authors()
        if isinstance(s, basestring):
            return s.lower()
        return ''


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

    # XXX PMR1 display mode compatibility hack
    security.declareProtected(View, 'pmr1_citation_authors')
    def pmr1_citation_authors(self):
        return self.Title()

    security.declareProtected(View, 'pmr1_citation_title')
    def pmr1_citation_title(self):
        return self.Description()


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
        # XXX-1
        #
        # There has been confusion as to why we set the Title like so.
        # Originally, I was going to have these title generated from the
        # object type, such that i18n can be supported.  I supposed I
        # could override getTitle to achieve that, but due to time
        # constraints I set title like so.
        #
        # Anyway, the intention is that the Plone rendering elements
        # (such as breadcrumbs, navigation) will look fine, example:
        # Models > Exposure > (model) > Model Metadata  
        #
        # However, this raised the question of search results - this
        # "flaw" is visibly manifested especially for 'Model Metadata',
        # where the indexed object would be that (by default), and so
        # search results would return a long list of documents with
        # that text as the title, which is non-sensical.
        #
        # One of the proposed workaround to do that is to do something
        # like:
        # self.setTitle(u'Documentation - %s' % self.origin)
        # or the title of the citation found in the meta object.  This
        # however will break breadcrumbs so it is not advisable.
        #
        # tl;dr: we are stuck with the following lines of code.
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
        # See: XXX-1
        self.setTitle(u'Mathematics')
        self.setDescription(u'Generated from %s' % self.origin)
        self.setContentType('text/html')
        self.setText(u'')

        # XXX we have to do some post processing here as the output from
        # the CellML to MathML XSLT includes the html headers.  Since 
        # the output is simple and predictable, we take substring.
        mathml = self._convert().decode('utf-8')
        start = mathml.find('<body>')
        end = mathml.find('</body>')
        if start < 0 or end < 0:
            self.mathml = u''
        else:
            # XXX len('<body>') == 6
            self.mathml = mathml[start + 6:end]


class ExposureCmetaDocument(ExposureDocument):
    """\
    Contains a rendering of the CellML Metadata.
    """
    # XXX this class should be part of the metadata, and registered into
    # some sort of database that will automatically load this up into
    # one of the valid document types that can be added.

    interface.implements(IExposureCmetaDocument)
    security = ClassSecurityInfo()

    metadata = fieldproperty.FieldProperty(IExposureCmetaDocument['metadata'])
    citation_authors = fieldproperty.FieldProperty(IExposureCmetaDocument['citation_authors'])
    citation_title = fieldproperty.FieldProperty(IExposureCmetaDocument['citation_title'])
    citation_bibliographicCitation = fieldproperty.FieldProperty(IExposureCmetaDocument['citation_bibliographicCitation'])
    citation_id = fieldproperty.FieldProperty(IExposureCmetaDocument['citation_id'])
    citation_issued = fieldproperty.FieldProperty(IExposureCmetaDocument['citation_issued'])
    keywords = fieldproperty.FieldProperty(IExposureCmetaDocument['keywords'])

    security.declareProtected(ModifyPortalContent, 'generate_content')
    def generate_content(self):
        # See: XXX-1
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

        # XXX ad-hoc sanity checking
        issued = citation[0]['issued']
        if pmr2.app.util.simple_valid_date(issued):
            self.citation_issued = issued
        else:
            # XXX could attempt to derive from workspace id, because
            # pmr1 export was done so that the date is retained
            # however this will hide issues in metadata...
            self.citation_issued = u''

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
        http = pmr2.app.util.uri2http(self.citation_id)
        if http:
            return '<a href="%s">%s</a>' % (http, self.citation_id)
        return self.citation_id

    def _get_authors_family_index(self):
        if self.citation_authors:
            return [pmr2.app.util.normal_kw(i[0]) 
                    for i in self.citation_authors]
        else:
            return []

    def _get_citation_title_index(self):
        if self.citation_title:
            return pmr2.app.util.normal_kw(self.citation_title)

    def _get_keywords_index(self):
        if self.keywords:
            results = [pmr2.app.util.normal_kw(i[1]) for i in self.keywords]
            results.sort()
            return results
        else:
            return []

    def keywords_string(self):
        return ', '.join(self._get_keywords_index())

    # XXX PMR1 display mode compatibility hack
    def _pmr1_citation_authors(self):
        if self.citation_authors and self.citation_issued:
            authors = u', '.join([i[0] for i in self.citation_authors])
            return u'%s, %s' % (authors, self.citation_issued[:4])
        else:
            # XXX just the prettified workspace id
            return aq_parent(self).workspace.replace('_', ', ').title()

    def _pmr1_citation_title(self):
        if self.citation_title:
            return self.citation_title
        else:
            return u''


class ExposureCodeDocument(ExposureDocument):
    """\
    Wrapper to display code.
    """

    interface.implements(IExposureCodeDocument)
    security = ClassSecurityInfo()

    raw_code = fieldproperty.FieldProperty(IExposureCodeDocument['raw_code'])

    security.declareProtected(ModifyPortalContent, 'generate_content')
    def generate_content(self):
        # See: XXX-1
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
        citation_title = None
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

            # XXX cheap way to get citation title
            if i == u'ExposureCmetaDocumentFactory' and obj.citation_title:
                citation_title = obj.citation_title
                self.title = obj.citation_title

        self.subdocument = subdoc

        # XXX this is a big hack that was requested because the metadata
        # of the models in the original PMR uses paper title for title
        # of the model, and variants were just numbers.  Now that they
        # are grouped together in a single exposure, there needs to be
        # some way to give them meaningful pointers in the title to show
        # which model is what.  Since there is no metadata field for
        # this purpose (i.e. model title should not use citation but
        # perhaps a dc:title in node about model), we use the file name.
        # 
        # However, this may or may not work, since these tags and names
        # can arbitrarily choosen as there will no longer be an
        # automated naming scheme in place, Here are some sanity checks.

        workspace = parent.workspace
        filename = self.origin

        if citation_title is not None and \
                re.search('_[0-9]{4}$', workspace) and \
                filename.startswith(workspace):
            # If we have a proper citation title (not based on name of
            # file), workspace name matches the PMR1 naming convention
            # and filename includes that fragment, check for the 
            # fragment.  Derive fragment from filename if we have a
            # match.
            fragment = filename[len(workspace):]
            if fragment.startswith('_'):
                fragment = fragment[1:]
            fragment = fragment.rsplit('.', 1)[0]
            if fragment:
                self.title = u'%s (%s)' % (self.title, fragment)

        # There was a demand requiring the list of authors to be 
        # displayed somehow.  We first test whether pmr1 citation title
        # can be retrieved (which is from the Cmeta sibling).  If not, 
        # we assume the parent will have the proper title set (which is
        # generated (guessed) by PMR1 migration from the file name).

        # Since the parent object may have the wrong title generated,
        # we set that title with our description, and then the 
        # description would be the title of this object.

        # citation authors list first
        cite_authors = self.pmr1_citation_authors()
        if cite_authors:
            # update title in parent here since we have it
            parent.setTitle(cite_authors)
        if not cite_authors:
            cite_authors = parent.Title()
        self.setDescription(cite_authors)

        # now we do citation title for the parent
        if citation_title is not None:
            parent.setDescription(citation_title)
            parent.reindexObject()

        # Add citation title into description of subobjects if it was
        # found.
        if citation_title is not None:
            for id_ in self.subdocument:
                if id_ not in parent:
                    # Something wrong.
                    continue
                ctx = parent[id_]
                ctx.setDescription(u'Citation Title: %s, %s' % 
                    (citation_title, ctx.Description()))
                ctx.reindexObject()

    def _get_subdoc_obj(self, factory, attr, default=None):
        # XXX this method cannot use catalog as this is used to return
        # the subobjects themselves during indexing.  Please do not use 
        # this method as the current implementation is clearly not
        # optimized, and avoid using the methods that depend on this
        # for the same reason.  Use the catalog to retrieve the desired
        # results as it will be much faster.
        try:
            # should create/use adapter adapt self to the desired
            # object through standardized set of names instead of 
            # creating the dictionary here as always.
            lookup = dict(zip(self.factories, self.subdocument))
            id = lookup[factory]
            o = self.aq_parent[id]
            result = getattr(o, attr)
        except:
            # we failed to get the value we want
            return default

        if hasattr(result, '__call__'):
            return result()
        else:
            return result

    security.declareProtected(View, 'get_documentation')
    def get_documentation(self):
        # XXX since we do not want to keep two copies of the text, we
        # will have to wake up the documentation object to get the text.
        return self.getText()

    security.declareProtected(View, 'get_pmr1_curation')
    def get_pmr1_curation(self):
        pairs = (
            ('pmr_curation_star', u'Curation Status:'),
            ('pmr_pcenv_star', u'OpenCell:'),
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

    # Let catalog index the documentation since this object provide it
    # by proxy.
    security.declareProtected(View, 'getText')
    def getText(self):
        return self._get_subdoc_obj(u'ExposurePMR1DocumentFactory',
            'getText', u'')

    security.declareProtected(View, 'SearchableText')
    def SearchableText(self):
        return self._get_subdoc_obj(u'ExposurePMR1DocumentFactory',
            'SearchableText', u'')

    # To generate prettier search results, we will need to do grab the
    # data from the metadata object and return it in here, too.
    # See: XXX-1

    security.declareProtected(View, 'get_authors_family_index')
    def get_authors_family_index(self):
        return self._get_subdoc_obj(u'ExposureCmetaDocumentFactory',
            '_get_authors_family_index', ())

    security.declareProtected(View, 'get_citation_title_index')
    def get_citation_title_index(self):
        return self._get_subdoc_obj(u'ExposureCmetaDocumentFactory',
            '_get_citation_title_index', ())

    security.declareProtected(View, 'get_keywords_index')
    def get_keywords_index(self):
        return self._get_subdoc_obj(u'ExposureCmetaDocumentFactory',
            '_get_keywords_index', ())

    security.declareProtected(View, 'pmr1_citation_authors')
    # XXX PMR1 display mode compatibility hack
    def pmr1_citation_authors(self):
        return self._get_subdoc_obj(u'ExposureCmetaDocumentFactory',
            '_pmr1_citation_authors', u'')

    security.declareProtected(View, 'pmr1_citation_title')
    def pmr1_citation_title(self):
        # Since this is normally processed from metadata to include the
        # variant fragment text. 
        return self.title
        #return self._get_subdoc_obj(u'ExposureCmetaDocumentFactory', 
        #    '_pmr1_citation_title', u'')
