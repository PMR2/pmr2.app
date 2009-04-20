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
from Products.CMFCore.permissions import View
from Products.PortalTransforms.data import datastream

import pmr2.mercurial
import pmr2.mercurial.utils

from pmr2.processor.cmeta import Cmeta

from pmr2.app.interfaces import *
from pmr2.app.mixin import TraversalCatchAll


class ExposureContainer(ATBTreeFolder):
    """\
    Container for exposures in PMR2.
    """

    interface.implements(IExposureContainer)

    def __init__(self, oid='exposure', **kwargs):
        super(ExposureContainer, self).__init__(oid, **kwargs)

    def get_path(self):
        # XXX quickie code
        #"""See IWorkspaceContainer"""

        p = aq_parent(aq_inner(self)).repo_root
        if not p:
            return None
        # XXX magic string
        return os.path.join(p, 'workspace')


class Exposure(ATFolder, TraversalCatchAll):
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

    security.declareProtected(View, 'get_path')
    def get_path(self):
        """See IExposure"""

        # aq_inner needed to get out of form wrappers
        p = self.get_parent_container().get_path()  # XXX get_path = quickie
        if not p:
            return None
        return os.path.join(p, self.workspace)

    security.declareProtected(View, 'get_log')
    def get_log(self, rev=None, branch=None, shortlog=False, datefmt=None):
        """See IExposure"""

        # XXX valid datefmt values might need to be documented/checked
        storage = self.get_storage()
        return storage.log(rev, branch, shortlog, datefmt).next()

    security.declareProtected(View, 'get_storage')
    def get_storage(self):
        """See IExposure"""

        path = self.get_path()
        return pmr2.mercurial.Storage(path)

    security.declareProtected(View, 'get_manifest')
    def get_manifest(self):
        storage = self.get_storage()
        return storage.raw_manifest(self.commit_id)

    security.declareProtected(View, 'get_file')
    def get_file(self, path):
        storage = self.get_storage()
        return storage.file(self.commit_id, path)

    security.declareProtected(View, 'get_parent_container')
    def get_parent_container(self):
        """\
        returns the container object that stores this.
        """

        result = aq_parent(aq_inner(self))
        return result

    security.declareProtected(View, 'get_pmr2_container')
    def get_pmr2_container(self):
        """\
        returns the root pmr2 object that stores this.
        """

        result = aq_parent(self.get_parent_container())
        return result

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

    security.declarePublic('get_exposure_workspace')
    def get_exposure_workspace(self):
        return self.workspace

    security.declareProtected(View, 'resolve_path')
    def resolve_path(self, filepath, view=None, validate=True):
        if not view:
            # XXX magic?
            view = '@@rawfile'

        if validate:
            storage = self.get_storage()
            try:
                test = storage.fileinfo(self.commit_id, filepath).next()
            except:  # PathNotFound
                return None

        result = '/'.join([
            self.get_pmr2_container().absolute_url(),
            'workspace',  # XXX magic!  should have method to return url
            self.workspace,
            view,
            self.commit_id,
            filepath,
        ])
        return result


class ExposureDocument(ATDocument):  #, TraversalCatchAll):
    """\
    Documentation for an exposure.
    """

    interface.implements(IExposureDocument)

    origin = fieldproperty.FieldProperty(IExposureDocument['origin'])
    transform = fieldproperty.FieldProperty(IExposureDocument['transform'])
    metadoc = fieldproperty.FieldProperty(IExposureDocument['metadoc'])

    def _convert(self):
        # this grabs contents of file from workspace (hg)
        input = aq_parent(self).get_file(self.origin)
        pt = getToolByName(self, 'portal_transforms')
        stream = datastream('processor')
        pt.convert(self.transform, input, stream)
        return stream.getData()

    def generate_content(self):
        self.setTitle(u'Documentation')
        self.setDescription(u'Generated from %s' % self.origin)
        self.setContentType('text/html')
        self.setText(self._convert())

    def get_curation_index(self):
        # XXX hack to make this not indexed by curation index
        return []

    def get_exposure_workspace(self):
        # XXX hack to make this not indexed by curation index
        return []

    def get_subdocument_structure(self):
        parent = self.aq_inner.aq_parent
        if self.metadoc and self.metadoc in parent:
            metadoc = parent[self.metadoc]
            docstruct = metadoc.get_subdocument_structure()
            return docstruct


class ExposureMetadoc(BrowserDefaultMixin, BaseContent):

    interface.implements(IExposureMetadoc)

    origin = fieldproperty.FieldProperty(IExposureMetadoc['origin'])
    factories = fieldproperty.FieldProperty(IExposureMetadoc['factories'])

    def get_subdocument_structure(self):
        result = {}
        subdocs = []
        # XXX following is naive code
        parent = self.aq_inner.aq_parent
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



class ExposureMathDocument(ExposureDocument):
    """\
    Documentation for an exposure for use with MathML.
    """

    interface.implements(IExposureMathDocument)
    #origin = fieldproperty.FieldProperty(IExposureMathDocument['origin'])
    #transform = fieldproperty.FieldProperty(IExposureMathDocument['transform'])
    mathml = fieldproperty.FieldProperty(IExposureMathDocument['mathml'])

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

    metadata = fieldproperty.FieldProperty(IExposureCmetaDocument['metadata'])
    citation_authors = fieldproperty.FieldProperty(IExposureCmetaDocument['citation_authors'])
    citation_title = fieldproperty.FieldProperty(IExposureCmetaDocument['citation_title'])
    citation_bibliographicCitation = fieldproperty.FieldProperty(IExposureCmetaDocument['citation_bibliographicCitation'])
    citation_id = fieldproperty.FieldProperty(IExposureCmetaDocument['citation_id'])
    keywords = fieldproperty.FieldProperty(IExposureCmetaDocument['keywords'])

    def generate_content(self):
        self.setTitle(u'Model Metadata')
        self.setDescription(u'Generated from %s' % self.origin)
        self.setContentType('text/html')
        input = aq_parent(self).get_file(self.origin)

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

    def citation_authors_string(self):
        if not self.citation_authors:
            return u''
        middle = u'</li>\n<li>'.join(
            ['%s, %s %s' % i for i in self.citation_authors])
        return u'<ul>\n<li>%s</li>\n</ul>' % middle

    def citation_id_html(self):
        if not self.citation_id:
            return u''
        http = pmr2.app.util.infouri2http(self.citation_id)
        if http:
            return '<a href="%s">%s</a>' % (http, self.citation_id)
        return self.citation_id

    def get_authors_family_index(self):
        if self.citation_authors:
            return [i[0].lower() for i in self.citation_authors]
        else:
            return []

    def get_citation_title_index(self):
        if self.citation_title:
            return self.citation_title.lower()

    def get_keywords(self):
        if self.keywords:
            # XXX magical replace
            return [i[1].replace(' ', '_') for i in self.keywords]
        else:
            return []


class ExposureCodeDocument(ExposureDocument):
    """\
    Wrapper to display code.
    """

    interface.implements(IExposureCodeDocument)

    raw_code = fieldproperty.FieldProperty(IExposureCodeDocument['raw_code'])

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

    def generate_content(self):
        parent = self.aq_parent
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

    def get_documentation(self):
        lookup = dict(zip(self.factories, self.subdocument))
        id = lookup[u'ExposurePMR1DocumentFactory']
        return self.aq_parent[id].getText()

    def get_pmr1_curation(self):
        pairs = (
            ('pmr_curation_star', u'Curation Status:'),
            ('pmr_pcenv_star', u'PCEnv:'),
            ('pmr_jsim_star', u'JSim:'),
            ('pmr_cor_star', u'COR:'),
        )
        curation = self.aq_parent.curation
        if not curation:
            return []
        result = []
        for key, label in pairs:
            if key not in curation:
                continue
            result.append({
                'label': label,
                'stars': curation[key][0],  # first item or character
            })
        return result

    def get_file_access_uris(self):
        result = []
        download_uri = self.aq_parent.resolve_path(self.origin)
        if download_uri:
            result.append({'label': u'Download', 'href': download_uri})

        run_uri = self.aq_parent.resolve_path(
            self.origin, '@@pcenv', False)  # validated above.
        result.append({'label': u'Solve using PCEnv', 'href': run_uri})

        # since session files were renamed into predictable patterns, we 
        # can guess here.
        session_path = os.path.splitext(self.origin)[0] + '.session.xml'

        manifest = self.aq_parent.get_manifest()
        s_uri = self.aq_parent.resolve_path(session_path, '@@pcenv')
        if s_uri:
            result.append({'label': u'Solve using Session File', 'href': s_uri})
        return result

    def workspace_uri(self):
        return self.aq_parent.resolve_path('', '@@file', False)
