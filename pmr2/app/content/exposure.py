import re
import os.path
from cStringIO import StringIO

from zope import interface
import zope.interface
import zope.component
from zope.schema import fieldproperty
from persistent import Persistent

from AccessControl import ClassSecurityInfo
from Acquisition import aq_parent, aq_inner
from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin
from Products.ATContentTypes.atct import ATCTContent
from Products.ATContentTypes.atct import ATFolder, ATBTreeFolder
from Products.ATContentTypes.atct import ATDocument
from Products.Archetypes.atapi import BaseContent
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.permissions import View, ModifyPortalContent
from Products.PortalTransforms.data import datastream

import pmr2.mercurial.interfaces
from pmr2.processor.cmeta import Cmeta

from pmr2.app.interfaces import IPMR2GlobalSettings
from pmr2.app.interfaces import *
from pmr2.app.content.interfaces import *
from pmr2.app.atct import ATFolderDocument
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

    def get_exposure_commit_id(self):
        return ''

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

    def pmr2_exposure_commit_id(self):
        return self.get_exposure_commit_id()

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


class Exposure(ATFolderDocument, TraversalCatchAll):
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

    interface.implements(IExposure, IExposureObject)
    security = ClassSecurityInfo()
    # XXX the get_ methods are similar to IWorkspace.
    # best to define a common interface.

    workspace = fieldproperty.FieldProperty(IExposure['workspace'])
    commit_id = fieldproperty.FieldProperty(IExposure['commit_id'])
    curation = fieldproperty.FieldProperty(IExposure['curation'])
    docview_gensource = fieldproperty.FieldProperty(IExposure['docview_gensource'])
    docview_generator = fieldproperty.FieldProperty(IExposure['docview_generator'])

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

    security.declareProtected(View, 'get_keywords_index')
    def get_keywords_index(self):
        # XXX stub, see get_authors_family_index
        return ()

    security.declareProtected(View, 'get_exposure_root_title')
    def get_exposure_root_title(self):
        return self.Title()

    security.declareProtected(View, 'get_exposure_root_path')
    def get_exposure_root_path(self):
        return self.absolute_url_path()

    security.declareProtected(View, 'get_exposure_root_id')
    def get_exposure_root_id(self):
        return self.id

    security.declareProtected(View, 'get_exposure_commit_id')
    def get_exposure_commit_id(self):
        return self.commit_id

    # XXX PMR1 display mode compatibility hack
    security.declareProtected(View, 'pmr1_citation_authors')
    def pmr1_citation_authors(self):
        return self.Title()

    security.declareProtected(View, 'pmr1_citation_title')
    def pmr1_citation_title(self):
        return self.Description()


class ExposureFolder(ATFolderDocument, TraversalCatchAll):

    interface.implements(IExposureFolder, IExposureObject)
    docview_gensource = fieldproperty.FieldProperty(IExposureFolder['docview_gensource'])
    docview_generator = fieldproperty.FieldProperty(IExposureFolder['docview_generator'])

    def __before_publishing_traverse__(self, ob, request):
        TraversalCatchAll.__before_publishing_traverse__(self, ob, request)
        ATFolder.__before_publishing_traverse__(self, ob, request)


class ExposureFile(ATDocument, ExposureContentIndexBase):
    """\
    Generic object within an exposure that represents a file in the
    workspace, and as an anchor for adapted content.
    """

    interface.implements(
        IExposureObject,
        IExposureFile,
    )
    views = fieldproperty.FieldProperty(IExposureFile['views'])
    docview_gensource = fieldproperty.FieldProperty(IExposureFile['docview_gensource'])
    docview_generator = fieldproperty.FieldProperty(IExposureFile['docview_generator'])
    selected_view = fieldproperty.FieldProperty(IExposureFile['selected_view'])
    security = ClassSecurityInfo()

    security.declareProtected(View, 'raw_text')
    def raw_text(self):
        """\
        Fetches raw text of all notes that are annotate to this file.
        """

        results = []
        for view in self.views:
            ctxobj = zope.component.queryAdapter(self, name=view)
            if ctxobj is not None:
                results.append(ctxobj.raw_text())
        return '\n'.join(results)

    # and then we have to deal with being compatible with features that
    # comptability that can't be cleanly decoupled at all.

    def get_authors_family_index(self):
        # @@metadata
        note = zope.component.queryAdapter(self, name='cmeta')
        if not (note and note.citation_authors):
            return []
        return [pmr2.app.util.normal_kw(i[0]) for i in note.citation_authors]

    def get_citation_title_index(self):
        # @@metadata
        note = zope.component.queryAdapter(self, name='cmeta')
        if not (note and note.citation_title):
            return []
        return pmr2.app.util.normal_kw(note.citation_title)

    def get_keywords_index(self):
        # @@metadata
        note = zope.component.queryAdapter(self, name='cmeta')
        if not (note and note.keywords):
            return []
        results = [pmr2.app.util.normal_kw(i[1]) for i in note.keywords]
        results.sort()
        return results

    # ... of course, PMR1.
    security.declareProtected(View, 'pmr1_citation_authors')
    def pmr1_citation_authors(self):
        note = zope.component.queryAdapter(self, name='cmeta')
        if not (note and note.citation_authors and note.citation_issued):
            # grab the workspace id (from exposure) and fix it
            # XXX can't do this, because this is a catalog function.
            #sa = zope.component.getAdapter(self, IExposureSourceAdapter)
            #exposure, workspace, p = sa.source()
            ctx = aq_parent(self)
            while ctx is not None:
                if IExposure.providedBy(ctx):
                    return ctx.workspace.replace('_', ', ').title()
                ctx = aq_parent(ctx)
            return ''
        authors = u', '.join([i[0] for i in note.citation_authors])
        return u'%s, %s' % (authors, note.citation_issued[:4])

    security.declareProtected(View, 'pmr1_citation_title')
    def pmr1_citation_title(self):
        note = zope.component.queryAdapter(self, name='cmeta')
        if not (note and note.citation_title):
            return self.Title()
        return note.citation_title
