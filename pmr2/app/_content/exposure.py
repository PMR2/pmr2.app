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

import pmr2.mercurial

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

    security.declareProtected(View, 'get_workspace')
    def get_workspace(self):
        """
        Returns the workspace object this Exposure represents.
        """

        o = self.query_workspace()
        if not o:
            # try manually
            p = self.get_pmr2_container()
            if 'workspace' not in p:
                # XXX this really should be some sort of internal error.
                raise WorkspaceObjNotFoundError()
            ws = p['workspace']
            if self.workspace not in ws:
                raise WorkspaceObjNotFoundError()
            return ws['self.workspace']
        return o.getObject()

    security.declareProtected(View, 'query_workspace')
    def query_workspace(self):
        """\
        Query for the workspace object this Exposure represents using
        catalog.
        """

        catalog = getToolByName(self, 'portal_catalog')
        # XXX path assumption.
        path = '/'.join(self.getPhysicalPath()[0:-2] + ('workspace',))
        q = {
            'id': self.workspace,
            'path': {
                'query': path,
                'depth': 1,
            }
        }
        result = catalog(**q)
        # there should be only one such id in the workspace for this
        # unique result.
        if result:
            return result[0]

    security.declarePrivate('get_path')
    def get_path(self):
        """See IExposure"""

        return self.get_workspace().get_path()

    security.declarePrivate('get_storage')
    def get_storage(self):
        """See IExposure"""

        return self.get_workspace().get_storage()

    security.declarePrivate('get_log')
    def get_log(self, rev=None, branch=None, shortlog=False, datefmt=None):
        """See IExposure"""

        # XXX valid datefmt values might need to be documented/checked
        # XXX should really reuse workspace value, but we want to cache
        # value.  We should use adapters so these two classes can share
        # the adapter we don't have to worry about assigning self.values
        # in this class.
        storage = self.get_storage()
        return storage.log(rev, branch, shortlog, datefmt).next()

    security.declarePrivate('get_manifest')
    def get_manifest(self):
        # XXX see above
        storage = self.get_storage()
        return storage.raw_manifest(self.commit_id)

    security.declarePrivate('get_file')
    def get_file(self, path):
        # XXX see above
        storage = self.get_storage()
        return storage.file(self.commit_id, path)

    security.declareProtected(View, 'get_parent_container')
    def get_parent_container(self):
        """\
        returns the container object that stores this.
        """

        # aq_inner needed to get out of form wrappers
        result = aq_parent(aq_inner(self))
        return result

    security.declareProtected(View, 'get_pmr2_container')
    def get_pmr2_container(self):
        """\
        returns the root pmr2 object that stores this.
        """

        result = aq_parent(self.get_parent_container())
        return result

    security.declareProtected(View, 'resolve_uri')
    def resolve_uri(self, filepath=None, view=None, validate=True):
        """
        Returns URI to a location within the workspace this exposure is
        derived from.

        Parameters:

        filepath
            The path fragment to the desired file.  Examples:

            - 'dir/file' - Link to the file
                e.g. http://.../workspace/name/@@view/rev/dir/file
            - '' - Link to the root of the manifest
                e.g. http://.../workspace/name/@@view/rev/
            - None - The workspace "homepage"

            Default: None

        view
            The view to use.  @@file for the file listing, @@rawfile for
            the raw file (download link).  See browser/configure.zcml 
            for a listing of views registered for this object.

            Default: None (@@rawfile)

        validate
            Whether to validate whether filepath exists.

            Default: True
        """

        # XXX magic!  should have method to return the uri of the 
        # workspace container.
        frag = [
            self.get_pmr2_container().absolute_url(),
            'workspace',  
            self.workspace,
        ]

        if filepath is not None:
            # we only need to resolve the rest of the path here.
            if not view:
                # XXX magic?
                view = '@@rawfile'

            if validate:
                storage = self.get_storage()
                try:
                    test = storage.fileinfo(self.commit_id, filepath).next()
                except:  # PathNotFound
                    return None

            frag.extend([
                view,
                self.commit_id,
                filepath,
            ])

        result = '/'.join(frag)
        return result

    security.declareProtected(View, 'short_commit_id')
    def short_commit_id(self):
        return pmr2.app.util.short(self.commit_id)

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
        input = aq_parent(self).get_file(self.origin)
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

    security.declareProtected(View, 'get_subdocument_structure')
    def get_subdocument_structure(self):
        parent = self.aq_inner.aq_parent
        if self.metadoc and self.metadoc in parent:
            metadoc = parent[self.metadoc]
            docstruct = metadoc.get_subdocument_structure()
            return docstruct


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
            return [pmr2.app.util.normal_kw(i[1]) for i in self.keywords]
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

    security.declareProtected(View, 'get_file_access_uris')
    def get_file_access_uris(self):
        result = []
        download_uri = self.aq_parent.resolve_uri(self.origin)
        if download_uri:
            result.append({'label': u'Download', 'href': download_uri})

        run_uri = self.aq_parent.resolve_uri(
            self.origin, '@@pcenv', False)  # validated above.
        result.append({'label': u'Solve using PCEnv', 'href': run_uri})

        # since session files were renamed into predictable patterns, we 
        # can guess here.
        session_path = os.path.splitext(self.origin)[0] + '.session.xml'

        manifest = self.aq_parent.get_manifest()
        s_uri = self.aq_parent.resolve_uri(session_path, '@@pcenv')
        if s_uri:
            result.append({'label': u'Solve using Session File', 'href': s_uri})
        return result

    security.declareProtected(View, 'workspace_manifest_uri')
    def workspace_manifest_uri(self):
        return aq_parent(self).resolve_uri('', '@@file', False)

    security.declareProtected(View, 'workspace_home_uri')
    def workspace_home_uri(self):
        return aq_parent(self).resolve_uri(None)
