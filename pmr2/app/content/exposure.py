from zope import interface
import zope.component
from zope.schema import fieldproperty

from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.atct import ATFolder, ATBTreeFolder
from Products.ATContentTypes.atct import ATDocument
from Products.CMFCore.permissions import View

from pmr2.app.interfaces import *
from pmr2.app.content.interfaces import *
from pmr2.app.atct import ATFolderDocument
from pmr2.app.mixin import TraversalCatchAll


class ExposureContainer(ATBTreeFolder):
    """\
    Container for exposures in PMR2.
    """

    interface.implements(IExposureContainer)
    security = ClassSecurityInfo()

    def __init__(self, oid='exposure', **kwargs):
        super(ExposureContainer, self).__init__(oid, **kwargs)


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


class ExposureFolder(ATFolderDocument, TraversalCatchAll):

    interface.implements(IExposureFolder, IExposureObject)
    docview_gensource = fieldproperty.FieldProperty(IExposureFolder['docview_gensource'])
    docview_generator = fieldproperty.FieldProperty(IExposureFolder['docview_generator'])

    def __before_publishing_traverse__(self, ob, request):
        TraversalCatchAll.__before_publishing_traverse__(self, ob, request)
        ATFolder.__before_publishing_traverse__(self, ob, request)


class ExposureFile(ATDocument):
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
